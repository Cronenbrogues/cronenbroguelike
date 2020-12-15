import re

import adventurelib

from cronenbroguelike import util
from engine import ai
from engine import dice
from engine.globals import G
from engine import say
from engine import when


def enter_room(room):
    """Convenience function called at game start and when entering a room."""
    room.on_enter()
    _look()


def _look():
    if G.player.current_room.description:
        say.insayne(G.player.current_room.description)

    # TODO: Bespoke descriptions for all items and characters.
    # TODO: Fix a(n) problems throughout code base.
    for item in G.player.current_room.items:
        say.insayne(f"There is a(n) {item.name} lying on the ground.")
    for character in G.player.current_room.characters:
        if character is G.player:
            continue
        # TODO: Move these descriptions to the actor.
        say.insayne(
            f"There is a(n) {character.name} slobbering in the corner."
        )
    for corpse in G.player.current_room.corpses:
        say.insayne(f"The corpse of a(n) {corpse.name} molders here.")
    say.insayne(f'Exits are {", ".join(G.player.current_room.display_exits)}.')


@adventurelib.when("exit DIRECTION")
@adventurelib.when("go DIRECTION")
@adventurelib.when("proceed DIRECTION")
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
        # TODO: Replace enqueue_text with text events.
        say.insayne(f"You proceed {the_direction.display_description}.")
        G.player.current_room.on_exit()
        G.player.current_room = next_room
        enter_room(G.player.current_room)


@when.when("look")
def look():
    _look()


@adventurelib.when("stats")
def stats():
    lines = []
    name_str = f"{G.player.name}"
    lines.append(name_str)
    # TODO: Unfuck this for zalgo.
    lines.append("".join("-" for _ in name_str))
    for stat in G.player.all_stats():
        if hasattr(stat, "current_value"):
            lines.append(f"{stat.name:10}: {stat.current_value}/{stat.value}")
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


class _CheatException(Exception):
    pass


_STAT_PATTERN = re.compile(r"(\w+)\s+(\-?\d+)")


def _cheat_stat(stat, delta):
    stat = stat.lower()
    delta = int(delta)
    if stat == "heal":
        G.player.health.heal_or_harm(delta, cause="CHEATING")
    else:
        try:
            the_stat = getattr(G.player, stat)
        except:
            raise _CheatException
        else:
            the_stat.modify(delta)


_ABILITY_PATTERN = re.compile(r"add ability (\w+)")


def _cheat_ability(ability_name):
    from cronenbroguelike import ability

    try:
        to_add = getattr(ability, ability_name)
    except AttributeError:
        raise _CheatException
    else:
        G.player.add_ability(to_add())


@adventurelib.when("cheat CODE")
def cheat(code):
    # TODO: Make healing more general.
    matches = []
    match = _STAT_PATTERN.search(code)
    if match is not None:
        matches.append((_cheat_stat, match))

    match = _ABILITY_PATTERN.search(code)
    if match is not None:
        matches.append((_cheat_ability, match))

    for function, match in matches:
        try:
            function(*match.groups())
            break
        except _CheatException:
            pass

    else:
        say.insayne(
            "You attempt to pry open cosmic mysteries but fail. Your "
            "pitiful mind reels with the effort."
        )
        G.player.insanity.modify(15)


def _resolve_attack(attacker, attack):
    # TODO: Add equipment, different damage dice, etc.
    # TODO: Respect attack.method.
    defender = attack.target
    is_player = attacker is G.player
    if is_player:
        subj, obj = ["you", defender.name]
    else:
        subj, obj = [attacker.name, "you"]
    miss = "miss" if is_player else "misses"
    hit = "hit" if is_player else "hits"

    strength_mod = int((attacker.strength.value - 10) / 2)
    to_hit = strength_mod + dice.roll("1d20")
    if to_hit < (10 + (defender.stamina.value - 10) / 2):
        say.insayne(f"{subj.title()} {miss}.")

    else:
        damage = dice.roll("1d8") + strength_mod
        # TODO: How to organize messages better? Death also creates text, so
        # there should be a way to make sure the messages are ordered.
        say.insayne(f"{subj.title()} {hit} for {damage} damage!")
        defender.health.heal_or_harm(-1 * damage)


def _get_present_actor(actor_name):
    return G.player.current_room.characters.find(actor_name)


@when.when("ability ABILITY")
def ability(ability):
    ability_name = ability
    the_ability = G.player.abilities.get(ability_name)
    if the_ability is None:
        say.insayne("You know no such ability.")
    else:
        the_ability.activate()


@adventurelib.when("suicide")
@adventurelib.when("commit suicide")
@adventurelib.when("die")
@adventurelib.when("just die")
@adventurelib.when("hold breath forever")
@when.when("sit there and starve")
def suicide():
    say.insayne(
        "Realizing the futility of continuing, you resign yourself to death. You lie on the floor and await oblivion."
    )
    G.player.health.heal_or_harm(-G.player.health.value, cause="ennui")


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
        say.insayne(f"There is no {actor_name} here.")
        return

    if not defender.alive:
        say.insayne(
            f"In a blind fury, you hack uselessly at the {defender.name}'s corpse."
        )
        G.player.insanity.modify(10)
        return

    # TODO: Move this to player AI. Use defender as a "hint."
    _resolve_attack(G.player, ai.Attack(target=defender, method=None))
    for character in G.player.current_room.characters:
        assert character.ai is not None
        action = character.ai.choose_action(G.player.current_room)
        if action.attack is not None:
            _resolve_attack(character, action.attack)
        else:
            say.insayne(f"{character.name} makes no hostile motion.")


@when.when("talk ACTOR")
def talk(actor):
    # TODO: Collapse common functionality in attack.
    actor_name = actor  # Variable names are constrained by adventurelib.
    interlocutor = _get_present_actor(actor_name)
    if interlocutor is None:
        say.insayne(f"There is no {actor_name} here.")
        return

    # TODO: Yeah, this is very parallel to attacking. Maybe there should be
    # a more generic "choose action" function?
    action = interlocutor.ai.choose_action(interlocutor.current_room)
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

    character = G.player.current_room.characters.find(item_name)
    if character is not None:
        # TODO: Collapse this with descriptive text in look().
        say.insayne(f"There is a(n) {character.name} slobbering in the corner.")
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
    else:
        book.read(G.player)


def _move_item(old_inventory, new_inventory, item):
    old_inventory.remove(item)
    new_inventory.add(item)


# TODO: Collapse with read?
# TODO: Could create a @when decorator in the item subclasses
# themselves that automatically registers a command.
# TODO: Refactor items; let items have "verb" objects which map to events.
@adventurelib.when("use ITEM", verb="use")
@adventurelib.when("eat ITEM", verb="eat")
@adventurelib.when("smoke ITEM", verb="smoke")
@when.when("consume ITEM", verb="consume")
def use(item, verb):
    item_name = item
    item = G.player.inventory.find(item_name)
    if item is None:
        say.insayne(f"You don't have a(n) {item_name}.")
        return
    try:
        item.consume(G.player)
    except AttributeError:
        say.insayne(f"You can't use the {item_name}.")


@adventurelib.when("take ITEM")
def take(item):
    item_name = item
    location, item = _find_in_room(item_name)
    if location is None or item is None:
        say.insayne(f"There is no {item_name} here to take.")
    else:
        say.insayne(f"You acquire the {item_name}.")
        _move_item(location, G.player.inventory, item)


@adventurelib.when("drop ITEM")
def drop(item):
    item_name = item
    item = G.player.inventory.find(item_name)
    if item is None:
        say.insayne(f"You don't have a(n) {item_name} to drop.")
    else:
        say.insayne(f"You drop the {item_name} on the ground.")
        _move_item(G.player.inventory, G.player.current_room.items, item)


@adventurelib.when("loot ITEM from CORPSE")
@when.when("loot CORPSE", item="everything")
def loot(item, corpse):
    item_name = item
    corpse_name = corpse
    character = _get_present_actor(corpse_name)

    # TODO: Really need some abstraction around combat turns to avoid this
    # duplication.
    if character is not None:
        message = "You cannot loot the living!"
        # TODO: What if none of the character present chooses to attack?
        if any(character.alive for character in G.player.current_room.characters):
            message += " All enemies attack as your clumsy pickpocketing attempt fails."
        say.insayne(message)
        for character in G.player.current_room.characters:
            if not character.alive:
                continue
            assert character.ai is not None
            action = character.ai.choose_action(G.player.current_room)
            if action.attack is not None:
                _resolve_attack(character, action.attack)
        return

    # TODO: This is duplicated from above. Maybe an "interact" function is
    # called for?
    corpse = G.player.current_room.corpses.find(corpse_name)
    if corpse is None:
        say.insayne(f"There is no {corpse_name} here.")

    else:
        if item_name in {"all", "everything"}:
            items = {item.name: item for item in corpse.inventory}
        else:
            items = {item_name: [corpse.inventory.find(item_name)]}
        for name, item in items.items():
            if item is None:
                say.insayne(f"There is no {item.name} on the corpse.")
            else:
                _move_item(corpse.inventory, G.player.inventory, item)
                say.insayne(f"You liberate {item.name} from the corpse.")
