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

## Release

Simply push a new annotated tag, and the configured Github Actions will trigger a new build + package + release cycle.

```
git tag -a v2 -m "Awesome new feature!"
```
