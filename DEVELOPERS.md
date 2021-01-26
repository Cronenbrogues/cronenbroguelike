# Developer Tricks

Here are a few features which are useful when manually testing the game.

## Logging

To configure logging, `cp logging_config.json.example logging_config.json` in the root `cronenbroguelike` directory (i.e., sibling to this file). This file recognizes the following parameters:

- `log_level`: a string identifying one of the Python `logging` module's log levels ("INFO," "DEBUG," etc.).

Set `log_level` to "DEBUG" to see log output. An example `logging_config.json` looks like

{"log\_level": "DEBUG"}

## Game Config

To enable various gameplay tweaks, `cp game_config.json.example game_config.json` in the root `cronenbroguelike` directory. This file recognizes the following parameters:

- `num_rooms`: an integer specifying how many rooms to place in the floor.
- `extra_commands`: a Boolean specifying whether to add various extra commands, including [cheat](#cheats).
- `random_run`: a Boolean specifying whether to let the game play itself by producing random commands.

`num_rooms` can be helpful to restrict the size of randomly generated floors when testing. `extra_commands`'s primary utility lies in the [cheat](#cheats) command, which allows the player to alter the player character's statistics and abilities. `random_run` is mostly for fun.

## Cheats

Those that would seek arcana must be inducted into the esoteric circle. Petition @flosincapite for initiation.

## Contact

Join us on [Discord](https://discord.gg/fTsr5EfeQf) or shoot an email to cronenbrogues@googlegroups.com.
