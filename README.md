# cronenbroguelike

A body horror roguelike text adventure game

## Play

Releases for MacOS, Windows and Linux can be found on the [releases page](https://github.com/Cronenbrogues/cronenbroguelike/releases).

## Develop

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m cronenbroguelike
```

See [DEVELOPERS.md](DEVELOPERS.md) for more details.

## Release

Simply push a new annotated tag, and the configured Github Actions will trigger a new build + package + release cycle.

```
git tag -a 2.0.0 -m "Added the office floor"
```

This project does NOT conform to [SemVer](https://semver.org/); we only push a new major version when a new floor is added.
