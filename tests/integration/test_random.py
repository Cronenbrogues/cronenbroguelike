import pytest

from cronenbroguelike import game

random_config = {
    "num_rooms": 15,
    "extra_commands": False,
    "random_run": 5000,
}


def test_random_run():
    game._run_game(random_config)
