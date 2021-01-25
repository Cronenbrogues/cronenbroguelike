import adventurelib

from whimsylib.item import Book
from whimsylib import ai
from whimsylib import dice
from whimsylib.globals import G
from whimsylib import say
from whimsylib import when


def enter_room(room):
    """Convenience function called at game start and when entering a room."""
    room.on_enter()
    # TODO: Heal psyche more slowly. Peg this to turns (also not yet implemented).
    G.player.psyche.heal_or_harm(1, do_log=False)
    _look()


def _look():
    if G.player.current_room.description:
        say.insayne(G.player.current_room.description)

    # TODO: Bespoke descriptions for all items and characters.
    for item in G.player.current_room.items:
        say.insayne(item.idle_description)
    for character in G.player.current_room.npcs:
        say.insayne(character.idle_text)
    for corpse in G.player.current_room.corpses:
        say.insayne(f"The corpse of {say.a(corpse.name)} molders here.")
    say.insayne(f'Exits are {", ".join(G.player.current_room.display_exits)}.')


@adventurelib.when("go DIRECTION")
@adventurelib.when("north", direction="north")
@adventurelib.when("south", direction="south")
@adventurelib.when("east", direction="east")
@when.when("west", direction="west")
def go(direction):
    direction = direction.lower()
    next_room, the_direction = G.player.current_room.exit(direction)
    if next_room is None:
        say.insayne(f"It is not possible to proceed {direction}.")
    else:
        say.insayne(f"You proceed {the_direction.display_description}.")
        G.player.current_room.on_exit()
        enter_room(next_room)


@when.when("look")
def look():
    # _look() before processing npc actions;
    # see https://github.com/flosincapite/cronenbroguelike/issues/69 (nice)
    _look()

    for character in G.player.current_room.npcs:
        if G.just_died:
            return
        assert character.ai is not None
        action = character.ai.choose_action(G.player.current_room)
        if action.attack is not None:
            _resolve_attack(character, action.attack)
        elif action.event is not None:
            if action.event.event is not None:
                action.event.event.execute()


@adventurelib.when("stats")
def stats():
    lines = []
    name_str = f"{G.player.name}"
    lines.append(name_str)
    # TODO: Unfuck this for zalgo.
    lines.append("".join("-" for _ in name_str))
    for stat in G.player.all_stats():
        if hasattr(stat, "maximum"):
            lines.append(f"{stat.name:10}: {stat.value}/{stat.maximum}")
        else:
            lines.append(f"{stat.name:10}: {stat.value}")
    lines.append("".join("-" for _ in name_str))
    lines.append("- abilities -")
    for ability_name, ability in sorted(G.player.abilities.items()):
        if ability_name:
            lines.append(f"{ability_name}: {ability.DESCRIPTION}")

    for i, line in enumerate(lines):
        add_newline = i == 0
        say.insayne(line, add_newline=add_newline)


@adventurelib.when("inventory")
def inventory():
    say.insayne("You possess the following:")
    if not G.player.inventory:
        say.insayne("Nothing.", add_newline=False)
        return
    # TODO: This is repeated in inspect(). Collapse these into a single function.
    for item in G.player.inventory:
        say.insayne(item.description, add_newline=False)


def _resolve_attack(attacker, attack):
    # TODO: Add equipment, different damage dice, etc.
    # TODO: Respect attack.method.
    defender = attack.target
    is_player = attacker is G.player
    if is_player:
        subj, obj = ["you", defender.name]
    else:
        subj, obj = [attacker.name, "you"]
    subj = say.capitalized(subj)
    miss = "miss" if is_player else "misses"
    hit = "hit" if is_player else "hits"

    strength_mod = int((attacker.strength.value - 10) / 2)
    to_hit = strength_mod + dice.roll("1d20")
    if to_hit < (10 + (defender.stamina.value - 10) / 2):
        say.insayne(f"{subj} {miss}.")

    else:
        damage = dice.roll("1d8") + strength_mod
        # TODO: How to organize messages better? Death also creates text, so
        # there should be a way to make sure the messages are ordered.
        say.insayne(f"{subj} {hit} {obj} for {damage} damage!")
        # TODO: Attack should have associated text which is consulted here.
        defender.health.heal_or_harm(
            -1 * damage, cause=f"the fins of {say.a(attacker.name)}"
        )

    if not (is_player or defender.alive):
        G.just_died = True


def _get_present_actor(actor_name):
    return G.player.current_room.npcs.find(
        actor_name
    ) or G.player.current_room.corpses.find(actor_name)


@when.when("ability ABILITY")
def ability(ability):
    ability_name = ability
    the_ability = G.player.abilities.get(ability_name)
    if the_ability is None:
        say.insayne("You know no such ability.")
    else:
        the_ability.activate()


@when.when("suicide")
def suicide():
    say.insayne(
        "Realizing the futility of continuing, you resign yourself to death. You lie on the floor and await oblivion."
    )
    G.player.health.heal_or_harm(-G.player.health.value, cause="succumbing to ennui")


@when.when("attack ACTOR")
def attack(actor):
    """Attacks another character in the same room."""
    actor_name = actor  # Variable names are constrained by adventurelib.
    # TODO: Consider turn order--some kind of agility stat?
    # TODO: Other actions should be considered "combat" actions. Implement some
    # notion of turns.
    # TODO: Other combat actions--spells, items, fleeing, etc.
    # TODO: Affinity/factions so monsters can choose whom to strike.
    defender = _get_present_actor(actor_name)
    if defender is None:
        say.insayne(f"There is no {actor_name} here to attack.")
        return

    if not defender.alive:
        say.insayne(
            f"In a blind fury, you hack uselessly at the {defender.name}'s corpse."
        )
        G.player.insanity.heal_or_harm(10)
        return

    # TODO: Move this to player AI. Use defender as a "hint."
    # TODO: Migrating to player AI will avoid the special-casing of Room.npcs.
    # TODO: Migrating to player AI can also allow for a more nuanced
    # menu when attacking.
    _resolve_attack(G.player, ai.Attack(target=defender, method=None))
    for character in G.player.current_room.npcs:
        if G.just_died:
            return
        assert character.ai is not None
        action = character.ai.choose_action(G.player.current_room, impulse="attack")
        if action.attack is not None:
            _resolve_attack(character, action.attack)
        elif action.speak is not None:
            say.insayne(action.speak.message)
        elif action.event is not None:
            action.event.event.execute()
        else:
            say.insayne(f"{say.capitalized(character.name)} makes no hostile motion.")


@when.when("talk ACTOR")
def talk(actor):
    # TODO: Collapse common functionality in attack.
    actor_name = actor  # Variable names are constrained by adventurelib.
    interlocutor = _get_present_actor(actor_name)
    if interlocutor is None:
        if _find_available_item(actor_name) is not None:
            if G.player.insanity.value > 30:
                say.insayne(
                    f"You talk to {actor_name} at length. In response, "
                    "it expatiates on the nature of reality. It's making "
                    f"a lot of sense, that talking {actor_name}."
                )
                G.player.insanity.heal_or_harm(15)
            else:
                say.insayne(f"Why are you talking to {actor_name}, crazy?")
                G.player.insanity.heal_or_harm(5)
        else:
            say.insayne(f"There is no {actor_name} here to talk to.")
        return

    if not interlocutor.alive:
        # TODO: Actors/items should have a "definite article" form.
        say.insayne(f"The corpse of {interlocutor.name} is a poor conversationalist.")
        return

    # TODO: Yeah, this is very parallel to attacking. Maybe there should be
    # a more generic "choose action" function?
    action = interlocutor.ai.choose_action(interlocutor.current_room, impulse="talk")
    if action.attack is not None:
        attack = action.attack
        assert attack.target is G.player
        say.insayne(f"The {interlocutor.name} has no interest in talking and attacks!")
        # TODO: _resolve_attack should accept the attack action as parameter.
        _resolve_attack(interlocutor, attack)

    elif action.speak is not None:
        say.insayne(action.speak.message)

    elif action.event is not None:
        action.event.event.execute()


@adventurelib.when("inspect ITEM")
def inspect(item):
    item_name = item  # Variable names are constrained by adventurelib.

    room_item = G.player.current_room.items.find(item_name)
    if room_item is not None:
        say.insayne(room_item.description)
        return

    character = G.player.current_room.corpses.find(item_name)
    if character is not None:
        # TODO: How to deal with definite articles when actor's name is a
        # proper name?
        message = f"Searching the {character.name}'s corpse, you find "
        if not character.inventory:
            message += "only still flesh and the fug of early death."
            say.insayne(message)
            return
        message += "the following items: "
        say.insayne(message)
        for item in character.inventory:
            say.insayne(item.description, add_newline=False)
        return

    character = G.player.current_room.npcs.find(item_name)
    if character is not None:
        # TODO: Collapse this with descriptive text in look().
        say.insayne(character.idle_text)
        return

    say.insayne(f"There is no {item} here to inspect.")


def _find_in_room(item_name):
    room_item = G.player.current_room.items.find(item_name)
    if room_item is not None:
        return G.player.current_room.items, room_item

    for corpse in G.player.current_room.corpses:
        corpse_item = corpse.inventory.find(item_name)
        if corpse_item is not None:
            return corpse.inventory, corpse_item

    return None, None


def _find_available_item(item_name):
    # TODO: Store item <-> inventory relationship as two-way?
    inventory_item = G.player.inventory.find(item_name)
    if inventory_item is not None:
        return G.player.inventory, inventory_item
    return _find_in_room(item_name)


@when.when("read BOOK")
def read(book):
    book_name = book
    _, book = _find_available_item(book_name)
    if book is None:
        say.insayne(f"There is no {book_name} here to read.")
    elif not isinstance(book, Book):
        say.insayne(
            f"You stare intently at the {book_name} but, alas, fail to read it."
        )
    else:
        book.read(G.player)


def _move_item(
    loser_inventory,
    winner_inventory,
    item,
    relinquishment_message=None,
    acquisition_message=None,
):
    loser_inventory.remove(item, message=relinquishment_message)
    winner_inventory.add(item, message=acquisition_message)


# TODO: Collapse with read?
# TODO: Could create a @when decorator in the item subclasses
# themselves that automatically registers a command.
# TODO: Refactor items; let items have "verb" objects which map to events.
@when.when("use ITEM", verb="use")
def use(item, verb):
    item_name = item
    item = G.player.inventory.find(item_name)
    if item is None:
        say.insayne(f"You don't have {say.a(item_name)}.")
        return
    try:
        item.consume(G.player)
    except AttributeError:
        say.insayne(f"You can't {verb} the {item_name}.")


@adventurelib.when("take ITEM")
def take(item):
    item_name = item
    location, item = _find_in_room(item_name)
    if location is None or item is None:
        if G.player.current_room.npcs.find(item_name):
            say.insayne("You cannot take sentient beings.")
        elif G.player.current_room.corpses.find(item_name):
            say.insayne("The corpse would be too burdensome to carry.")
        else:
            say.insayne(f"There is no {item_name} here to take.")
    elif not item.obtainable:
        say.insayne("You can't take the {item_name}.")
    else:
        _move_item(location, G.player.inventory, item)


@adventurelib.when("drop ITEM")
def drop(item):
    item_name = item
    item = G.player.inventory.find(item_name)
    if item is None:
        say.insayne(f"You don't have {say.a(item_name)} to drop.")
    else:
        _move_item(
            G.player.inventory,
            G.player.current_room.items,
            item,
            relinquishment_message=f"You drop the {item_name} on the ground.",
        )


@adventurelib.when("loot CORPSE", item="everything")
@when.when("loot ITEM from CORPSE")
def loot(item, corpse):
    item_name = item
    corpse_name = corpse
    character = _get_present_actor(corpse_name)

    if character is None:
        say.insayne(f"There is no {corpse_name} here.")
        return

    # TODO: Really need some abstraction around combat turns to avoid this
    # duplication.
    if character.alive:
        message = "You cannot loot the living!"
        # TODO: What if none of the character present chooses to attack?
        if G.player.current_room.npcs:
            message += " All enemies attack as your clumsy pickpocketing attempt fails."
        say.insayne(message)
        for character in G.player.current_room.npcs:
            if G.just_died:
                return
            assert character.ai is not None
            action = character.ai.choose_action(G.player.current_room)
            if action.attack is not None:
                _resolve_attack(character, action.attack)
        return

    else:
        if item_name in {"all", "everything"}:
            items = character.inventory.items_by_name()
        else:
            items = {item_name: [character.inventory.find(item_name)]}
        for name, item_list in items.items():
            for item in item_list:
                if item is None:
                    say.insayne(f"There is no {name} on the corpse.")
                else:
                    _move_item(
                        character.inventory,
                        G.player.inventory,
                        item,
                        acquisition_message=f"You liberate {item.name} from the corpse.",
                    )
