from cronenbroguelike import rooms
from unittest.mock import patch
import pytest

# TODO: introduce some room test fixtures


@patch("cronenbroguelike.rooms._rooms_for_theme")
def test_get_rooms_default_number(rooms_patch):
    rooms_patch.return_value = [rooms._CathedralCatacombs] * 10
    room_list = rooms.get_rooms()
    assert len(room_list) == 10


@patch("cronenbroguelike.rooms._rooms_for_theme")
def test_get_rooms_limited_number(rooms_patch):
    rooms_patch.return_value = [rooms._CathedralCatacombs] * 10
    room_list = rooms.get_rooms(number=5)
    assert len(room_list) == 5


@patch("cronenbroguelike.rooms._rooms_for_theme")
def test_get_rooms_more_than_total(rooms_patch):
    rooms_patch.return_value = [rooms._CathedralCatacombs] * 10
    room_list = rooms.get_rooms(number=15)
    assert len(room_list) == 15


@patch("cronenbroguelike.rooms._rooms_for_theme")
def test_get_rooms_more_required_than_requested(rooms_patch):
    rooms_patch.return_value = [rooms._AltarRoom] * 2
    with pytest.raises(Exception):
        room_list = rooms.get_rooms(number=1)
