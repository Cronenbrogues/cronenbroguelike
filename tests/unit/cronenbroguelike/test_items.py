from unittest.mock import patch
import pytest

from whimsylib import actor

from cronenbroguelike import items


def test_create_ceremonial_knife():
    knife = items.CeremonialKnife.create()
    assert set(knife.aliases) == set(["ceremonial knife", "knife", "kris"])


def test_create_meditation_book():
    book = items.MeditationBook.create()
    assert set(book.aliases) == set(
        ["meditation tome", "meditation book", "tome", "book"]
    )


def test_read_meditation_book():
    book = items.MeditationBook.create()
    aliterate = actor.create_actor(10, 10, 10, 10, "aliterate")
    assert not aliterate.abilities
    book.read(aliterate)
    assert len(aliterate.abilities) == 1


@patch("cronenbroguelike.items.say.insayne")
def test_read_meditation_book_twice(mock_say):
    book = items.MeditationBook.create()
    aliterate = actor.create_actor(10, 10, 10, 10, "aliterate")
    aliterate.set_has_read(book)
    book.read(aliterate)
    mock_say.assert_called_once_with(
        "You have already tasted the wisdom distilled in this book."
    )
