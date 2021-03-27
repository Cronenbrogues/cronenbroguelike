from unittest.mock import patch
import pytest

from whimsylib import room

from cronenbroguelike import floor
from cronenbroguelike import rooms


class _ImportantRoom(room.Room):
    _DESCRIPTION = ""
    _THEMES = ""
    REQUIRED = True


def _vecinos(cámara):
    return set(
        [
            destino
            for destino, _ in [cámara.exit(salida) for salida in cámara.display_exits]
        ]
    )


def _BFS(planta):
    inicio = planta.random_room()
    no_visitados = set(planta._rooms.values())
    cola = [inicio]
    counter = 0
    while cola:
        actual = cola.pop(0)
        if actual not in no_visitados:
            continue
        counter += 1
        no_visitados.remove(actual)
        for vecino in _vecinos(actual):
            cola.append(vecino)
    return no_visitados


@patch("cronenbroguelike.rooms._rooms_for_theme")
def test_all_rooms_reachable(parche_cámaras):
    parche_cámaras.return_value = [_ImportantRoom] * 69 + [
        rooms._CathedralCatacombs
    ] * 420
    numero_de_cámaras = 200
    iglesia = floor.Floor.generate("catedral", numero_de_cámaras)
    assert numero_de_cámaras == len(iglesia._rooms)

    # Repite la prueba diez veces, cada vez de cámara distinta.
    for _ in range(10):
        no_visitados = _BFS(iglesia)
        assert not no_visitados
