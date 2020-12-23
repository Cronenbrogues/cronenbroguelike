import json
import random

import adventurelib

from . import commands
from . import floor
from . import npcs
from . import rooms
from engine import actor
from engine import ai
from engine import directions
from engine.event import Event as _Event
from engine.globals import G as _G
from engine.globals import poll_events as _poll_events
from engine import say
from engine import when


def _load_config():
    game_config = {"num_rooms": 15, "extra_commands": False}
    try:
        with open("game_config.json", "r") as inp:
            additional_config = json.load(inp)
    except FileNotFoundError:
        additional_config = {}
    game_config.update(additional_config)
    return game_config


def _create_rooms(number_of_rooms):
    return random.sample(rooms.all_rooms(), number_of_rooms)


def _get_random_start():
    # TODO: Condition this on how the last death actually occurred.
    death_text = _G.cause_of_death or random.choice(
        [
            "being impaled",
            "slowly suffocating as a glabrous tentacle horror looks on",
        ]
    )
    for text in [
        f"You recall your death by {death_text}. The memory fades away.",
        "You know only that you have been here for interminable years, "
        "that you have died innumerable times, and that someone once told "
        "you there was a way out. You were told this an eon ago, or maybe "
        "a day, but the stubborn hope of escape glisters in your mind.",
    ]:
        say.insayne(text)


class _ResetDiedFlag(_Event):

    def execute(self):
        _G.just_died = False
        self.kill()


def _start_game(_, config):

    def _restart(unused_actor):
        # Creates the player character and ensures game will restart upon death.
        _G.player = actor.create_actor(
            health=10,
            psyche=10,
            strength=10,
            stamina=10,
            will=10,
            wisdom=10,
            insanity=0,
            name="player",
        )
        _G.player.log_stats = True
        _G.player.upon_death(_restart)

        # Removes all events from global queue.
        _G.clear_queues()

        # Resets just_died flag.
        _G.add_event(_ResetDiedFlag(), "pre")

        # Creates a small dungeon.
        level = floor.Floor.generate("cathedral", number_rooms=config["num_rooms"])

        # Places a monster in a random room.
        level.random_room().add_character(npcs.fish_man())

        # Places an NPC in a random room.
        level.random_room().add_character(npcs.mad_librarian())

        # Places a cool NPC in a random room.
        level.random_room().add_character(npcs.smokes_man())

        # Places the player.
        level.random_room().add_character(_G.player)

        # Starts it up.
        _get_random_start()
        adventurelib.set_context("start_game")
        adventurelib.set_context(None)
        with _poll_events(poll_before=True, poll_after=True):
            commands.enter_room(_G.player.current_room)

    _restart(None)


def main():
    game_config = _load_config()
    if game_config.get("extra_commands"):
        from . import extra_commands
    adventurelib.say("")  # Necessary for space before first prompt.
    adventurelib.say(
            "Alex, you made it. I am glad you did. I am sorry you did. You will "
            "lose so, so much of yourself before you can leave again. I am glad "
            "you are here. I am sorry you are here.")
    adventurelib.say("")
    adventurelib.say("...")
    _start_game(None, game_config)
    adventurelib.say("")
    adventurelib.start()
