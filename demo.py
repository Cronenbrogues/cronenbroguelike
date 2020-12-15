import logging


def _load_config():
    import json

    config = {"log_level": "INFO", "num_rooms": 15}
    try:
        with open("config.json", "r") as inp:
            additional_config = json.load(inp)
    except FileNotFoundError:
        additional_config = {}

    config.update(additional_config)
    config["log_level"] = config["log_level"].upper()
    return config


CONFIG = _load_config()
logging.basicConfig(level=getattr(logging, log_level))


import random

import adventurelib

from cronenbroguelike import commands
from cronenbroguelike import floor
from cronenbroguelike import npcs
from cronenbroguelike import rooms
from engine import actor
from engine import ai
from engine import directions
from engine.globals import G
from engine import say
from engine import when


def _create_rooms(number_of_rooms):
    return random.sample(rooms.all_rooms(), number_of_rooms)


def _get_random_start():
    # TODO: Condition this on how the last death actually occurred.
    death_text = G.cause_of_death or random.choice(
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


def _start_game(_):
    @when.when("startgame", context="start_game", poll_after=True)
    def startgame():
        commands.enter_room(G.player.current_room)

    # Creates the player character and ensures game will restart upon death.
    G.player = actor.create_actor(
        health=10,
        psyche=10,
        strength=10,
        stamina=10,
        will=10,
        wisdom=10,
        insanity=0,
        name="player",
    )
    G.player.log_stats = True
    G.player.upon_death(startgame)

    # Creates a small dungeon.
    level = floor.Floor.generate("cathedral", number_rooms=CONFIG["num_rooms"])

    # Places a monster in a random room.
    level.random_room().add_character(npcs.fish_man())

    # Places an NPC in a random room.
    level.random_room().add_character(npcs.mad_librarian())

    # Places a cool NPC in a random room.
    level.random_room().add_character(npcs.smokes_man())

    # Places the player.
    level.random_room().add_character(G.player)

    # Starts it up.
    _get_random_start()
    adventurelib.set_context("start_game")
    startgame()
    adventurelib.set_context(None)


_start_game(None)
G.player.upon_death(_start_game)
adventurelib.say("")  # Necessary for space before first prompt.
adventurelib.start()
