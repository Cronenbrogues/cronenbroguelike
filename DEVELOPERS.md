# Developer Tricks

Here are a few features which are useful when manually testing the game.

## Logging

To configure logging, create `logging_config.json` in the root `cronenbroguelike` directory (i.e., sibling to this file). This file recognizes the following parameters:

- `log_level`: a string identifying one of the Python `logging` module's log levels ("INFO," "DEBUG," etc.).

Set `log_level` to "DEBUG" to see log output. See `logging_config.default.json` for an example.

## Game Config

To enable various gameplay tweaks, create `game_config.json` in the root `cronenbroguelike` directory.
You can do this easily by copying the default configuration e.g. 

```
cp game_config.default.json game_config.json
```

`game_config.json` recognizes the following parameters:

- `num_rooms`: an integer specifying how many rooms to place in the floor.
- `extra_commands`: a Boolean specifying whether to add various extra commands, including [cheat](#cheats).
- `random_run`: an integer specifying the number of rounds the game should randomly play itself, or null to play normally.

`num_rooms` can be helpful to restrict the size of randomly generated floors when testing. `extra_commands`'s primary utility lies in the [cheat](#cheats) command, which allows the player to alter the player character's statistics and abilities. `random_run` is mostly for fun and fuzzing.

## Cheats

Those that would seek arcana must be inducted into the esoteric circle. Petition @flosincapite for initiation.

## Contact

Join us on [Discord](https://discord.gg/fTsr5EfeQf) or shoot an email to cronenbrogues@googlegroups.com.
