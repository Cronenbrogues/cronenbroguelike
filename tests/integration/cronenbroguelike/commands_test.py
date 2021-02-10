import io
from unittest.mock import call
from unittest.mock import patch

from cronenbroguelike import ability

# Importing this file registers the commands, although the import looks unused.
from cronenbroguelike import commands  # pragma pylint: disable=unused-import
from whimsylib import actor
from whimsylib import directions
from whimsylib import start
from whimsylib.globals import G
from whimsylib.item import Item
from whimsylib.room import Room
from tests import common


_OrnateRoom = Room.create_room_type("_OrnateRoom", "This room is very opulent, dang.")


_SqualidRoom = Room.create_room_type("_SqualidRoom", "Poop is here.")


@patch("sys.stdin", new_callable=io.StringIO)
@patch("whimsylib.say.insayne")
class CommandsTest(common.EngineTest):
    def _run_commands(self, stdin, *commands):
        stdin.write("\n".join(commands))
        stdin.seek(0)
        start.start()

    def test_go_bad_direction(self, mock_say, mock_stdin):
        ornate = _OrnateRoom()
        ornate.add_character(G.player)
        self.assertIs(ornate, G.player.current_room)  # Precondition

        direction = directions.north
        description = direction.display_description
        next_room, _ = ornate.exit(description)
        self.assertIs(None, next_room)  # Precondition

        self._run_commands(mock_stdin, f"go {description}")
        mock_say.assert_called_once_with(
            f"It is not possible to proceed {description}."
        )

    @patch("whimsylib.room.Room.on_exit")
    @patch("whimsylib.globals.G.player.psyche.heal_or_harm")
    def test_go_right_track(self, mock_heal, mock_exit, mock_say, mock_stdin):
        ornate, squalid = _OrnateRoom(), _SqualidRoom()
        ornate.add_character(G.player)
        self.assertIs(ornate, G.player.current_room)  # Precondition

        direction = directions.purple
        description = direction.display_description
        ornate.add_exit(direction, squalid)
        next_room, _ = ornate.exit(description)
        self.assertIs(squalid, next_room)  # Precondition

        self._run_commands(mock_stdin, f"go {description}")

        mock_exit.assert_called_once()

        # Psyche is healed by 1 every time player enters a new room.
        mock_heal.assert_called_with(1, do_log=False)

        # This implies that squalid.on_enter() was called.
        self.assertIs(squalid, G.player.current_room)
        mock_say.assert_has_calls(
            [call(f"You proceed {description}."), call(squalid.description)]
        )

    def test_look(self, mock_say, mock_stdin):
        ornate, squalid = _OrnateRoom(), _SqualidRoom()
        ornate.add_character(G.player)
        self.assertIs(ornate, G.player.current_room)  # Precondition

        ornate.add_item(Item("fruit bag, you know, of fruit"))

        direction = directions.purple
        description = direction.display_description
        ornate.add_exit(direction, squalid)
        next_room, _ = ornate.exit(description)
        self.assertIs(squalid, next_room)  # Precondition

        self._run_commands(mock_stdin, "look")

        mock_say.assert_has_calls(
            [
                call("This room is very opulent, dang."),
                call("There is a fruit bag, you know, of fruit lying on the ground."),
                call("Exits are through a murky tunnel."),
            ]
        )

    def test_stats(self, mock_say, mock_stdin):
        self._run_commands(mock_stdin, "stats")
        mock_say.assert_has_calls(
            [
                call("player", add_newline=True),
                call("------", add_newline=False),
                call("health    : 10/10", add_newline=False),
                call("psyche    : 10/10", add_newline=False),
                call("insanity  : 0/100", add_newline=False),
                call("strength  : 10", add_newline=False),
                call("stamina   : 10", add_newline=False),
                call("------", add_newline=False),
                call("- abilities -", add_newline=False),
            ]
        )

    def test_different_stats(self, mock_say, mock_stdin):
        G.player = actor.create_actor(20, 20, 20, 20, "the flippin devil")
        G.player.health.heal_or_harm(-9)
        G.player.add_ability(ability.meditation())

        self._run_commands(mock_stdin, "stats")
        mock_say.assert_has_calls(
            [
                call("the flippin devil", add_newline=True),
                call("-----------------", add_newline=False),
                call("health    : 11/20", add_newline=False),
                call("psyche    : 20/20", add_newline=False),
                call("insanity  : 0/100", add_newline=False),
                call("strength  : 20", add_newline=False),
                call("stamina   : 20", add_newline=False),
                call("-----------------", add_newline=False),
                call("- abilities -", add_newline=False),
                call(
                    "meditation: Soothes the damaged mind; liberates the trapped soul.",
                    add_newline=False,
                ),
            ]
        )
