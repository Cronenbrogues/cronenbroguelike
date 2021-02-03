import random
import adventurelib

from . import commands
from . import floor
from . import npcs
from . import rooms
from . import util
from whimsylib import actor
from whimsylib import ai
from whimsylib import directions
from whimsylib.event import Event as _Event
from whimsylib.globals import G as _G
from whimsylib.globals import poll_events as _poll_events
from whimsylib import say
from whimsylib import tartarus
from whimsylib import when


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


def _restart(config):
    # Resets all global state (clears event queues, etc.).
    _G.reset()

    # Creates the player character and ensures game will restart upon death.
    _G.player = actor.create_actor(
        health=10,
        psyche=10,
        strength=10,
        stamina=10,
        name="player",
    )
    _G.player.log_stats = True

    # Resets just_died flag.
    _G.add_event(_ResetDiedFlag(), "pre")

    # Creates a small dungeon.
    level = floor.Floor.generate("cathedral", config["num_rooms"])

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
    with _poll_events(poll_before=True, poll_after=True):
        commands.enter_room(_G.player.current_room)


def _run_game(config):
    num_random_actions = 0
    if config.get("extra_commands") or config.get("random_run"):
        from . import extra_commands
    while True:
        try:
            _restart(config)
            adventurelib.say("")  # Necessary for space before first prompt.
            if config.get("random_run"):
                while num_random_actions < config.get("random_run"):
                    adventurelib._handle_command("random")
                    num_random_actions += 1
                if num_random_actions >= config.get("random_run"):
                    break
            adventurelib.start()
        except KeyboardInterrupt:
            adventurelib.say("☠ Farewell☠")
            return
        except tartarus.RaptureException:
            pass


def main():
    game_config = util.read_overridable_config("game_config.default.json")
    _run_game(game_config)
