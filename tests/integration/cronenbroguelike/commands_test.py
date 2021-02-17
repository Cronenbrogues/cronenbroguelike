import io
from unittest.mock import call
from unittest.mock import Mock
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


class CommandsTest(common.EngineTest):
    def setUp(self):
        super().setUp()
        self._parent = Mock()
        self._parent.pre = Mock()
        G.add_event(self._parent.pre, "pre")
        self._parent.post = Mock()
        G.add_event(self._parent.post, "post")

    def _run_commands(self, stdin, *commands):
        stdin.write("\n".join(commands))
        stdin.seek(0)
        start.start()

    def test_go_bad_direction(self):
        ornate = _OrnateRoom()
        ornate.add_character(G.player)
        self.assertIs(ornate, G.player.current_room)  # Precondition

        direction = directions.north
        description = direction.display_description
        next_room, _ = ornate.exit(description)
        self.assertIs(None, next_room)  # Precondition

        with patch("sys.stdin", new_callable=io.StringIO) as fake_stdin, patch(
            "whimsylib.say.insayne", self._parent.say
        ):
            self._run_commands(fake_stdin, f"go {description}")
            self._parent.assert_has_calls(
                [
                    call.pre.execute(),
                    call.say(f"It is not possible to proceed {description}."),
                    call.post.execute(),
                ]
            )

    def test_go_right_track(self):
        ornate, squalid = _OrnateRoom(), _SqualidRoom()
        ornate.add_character(G.player)
        self.assertIs(ornate, G.player.current_room)  # Precondition

        direction = directions.purple
        description = direction.display_description
        ornate.add_exit(direction, squalid)
        next_room, _ = ornate.exit(description)
        self.assertIs(squalid, next_room)  # Precondition

        with patch("sys.stdin", new_callable=io.StringIO) as fake_stdin, patch(
            "whimsylib.say.insayne", self._parent.say
        ), patch("whimsylib.room.Room.on_exit", self._parent.exit), patch(
            "whimsylib.globals.G.player.psyche.heal_or_harm", self._parent.heal
        ):

            self._run_commands(fake_stdin, f"go {description}")
            # This implies that squalid.on_enter() was called.
            self.assertIs(squalid, G.player.current_room)
            self._parent.assert_has_calls(
                [
                    call.pre.execute(),
                    call.say(f"You proceed {description}."),
                    call.exit(),
                    call.heal(1, do_log=False),
                    call.say(squalid.description),
                    call.say(f"Exits are {direction.opposite.display_description}."),
                    call.post.execute(),
                ]
            )

    def test_look(self):
        ornate, squalid = _OrnateRoom(), _SqualidRoom()
        ornate.add_character(G.player)
        self.assertIs(ornate, G.player.current_room)  # Precondition

        ornate.add_item(Item("fruit bag, you know, of fruit"))

        direction = directions.purple
        description = direction.display_description
        ornate.add_exit(direction, squalid)
        next_room, _ = ornate.exit(description)
        self.assertIs(squalid, next_room)  # Precondition

        with patch("sys.stdin", new_callable=io.StringIO) as fake_stdin, patch(
            "whimsylib.say.insayne", self._parent.say
        ):
            self._run_commands(fake_stdin, "look")
            self._parent.assert_has_calls(
                [
                    call.pre.execute(),
                    call.say("This room is very opulent, dang."),
                    call.say(
                        "There is a fruit bag, you know, of fruit lying on the ground."
                    ),
                    call.say("Exits are through a murky tunnel."),
                    call.post.execute(),
                ]
            )

    @patch("sys.stdin", new_callable=io.StringIO)
    @patch("whimsylib.say.insayne")
    def test_stats(self, mock_say, fake_stdin):
        self._run_commands(fake_stdin, "stats")
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

    @patch("sys.stdin", new_callable=io.StringIO)
    @patch("whimsylib.say.insayne")
    def test_different_stats(self, mock_say, fake_stdin):
        G.player = actor.create_actor(20, 20, 20, 20, "the flippin devil")
        G.player.health.heal_or_harm(-9)
        G.player.add_ability(ability.meditation())

        self._run_commands(fake_stdin, "stats")
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
