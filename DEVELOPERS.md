# Developer Tricks

Here are a few features which are useful when manually testing the game.

## Logging

To enable logging, create a file called `logging_config.json` in the root `cronenbroguelike` directory (i.e., a sibling to this file. This file recognizes the following parameters:

- `log_level`: a string identifying one of the Python `logging` module's log levels ("INFO," "DEBUG," etc.).

Set `log_level` to "DEBUG" to see log output. An example `logging_config.json` looks like

{"log\_level": "DEBUG"}

## Game Config

To enable various gameplay tweaks, create a file called `game_config.json` in the root `cronenbroguelike` directory. This file recognizes the following parameters:

- `num_rooms`: an integer specifying how many rooms to place in the floor.
- `extra_commands`: a Boolean specifying whether to add various extra commands, including [cheat](cheat).
- `random_run`: a Boolean specifying whether to let the game play itself by producing random commands.

`num_rooms` can be helpful to restrict the size of randomly generated floors when testing. `extra_commands`'s primary utility lies in the [cheat](cheat) command, which allows the player to alter the player character's statistics and abilities. `random_run` is mostly for fun.

## <a id="cheat">Cheats</a>

Those that would seek arcana, must be inducted into the esoteric circle. Petition @flosincapite for initiation.
