import collections
import logging
import random

from cronenbroguelike import rooms
from whimsylib import dice
from whimsylib import directions


# TODO: Make these a coordinate attribute?
_WIDTH = 21
_HEIGHT = 21


# TODO: What if we abandoned the conceit of a 2d plane and just let this be
# an arbitrary graph? That's some Cthulhu stuff.
class _Coordinate(collections.namedtuple("Coordinate", ["x", "y"])):
    @property
    def north(self):
        return _Coordinate(self.x, (self.y - 1) % _HEIGHT)

    @property
    def south(self):
        return _Coordinate(self.x, (self.y + 1) % _HEIGHT)

    @property
    def east(self):
        return _Coordinate((self.x + 1) % _WIDTH, self.y)

    @property
    def west(self):
        return _Coordinate((self.x - 1) % _WIDTH, self.y)


def _add_exit(room, next_room, direction_hint):
    room.add_exit(getattr(directions, direction_hint), next_room)


class Floor:
    def __init__(self, room_dict, name_to_room=None):
        self._rooms = room_dict
        if name_to_room is None:
            name_to_room = {}
        self._names = name_to_room

    def __getitem__(self, coordinate):
        return self._rooms[coordinate]

    def room_by_name(self, name):
        return self._names.get(name, None)

    def random_room(self):
        return random.choice(list(self._rooms.values()))

    @classmethod
    def generate(cls, theme, number_rooms=None):
        if theme == "office":
            return _generate_office()

        room_dict = {}
        room_list = rooms.get_rooms(number=number_rooms, theme=theme)
        start_coordinate = _Coordinate(10, 10)
        coordinate_queue = collections.deque()
        coordinate_queue.append(start_coordinate)

        for room in room_list:
            if not coordinate_queue:
                break
            if len(room_dict) >= number_rooms:
                break

            # Finds an unoccupied coordinate.
            while True:
                coordinate = coordinate_queue.popleft()
                if room_dict.get(coordinate) is None:
                    break

            # Creates a new room in that location.
            room_dict[coordinate] = room

            for direction in ["north", "south", "east", "west"]:
                new_coordinate = getattr(coordinate, direction)
                next_room = room_dict.get(new_coordinate)
                if next_room is None:
                    coordinate_queue.append(new_coordinate)

                else:
                    # Adds some exits.
                    if dice.roll("1d100") > 50:
                        _add_exit(room, next_room, direction)

        # Traverse room graph. If any rooms are not connected, use a
        # non-Euclidean entrance to address that.
        # TODO: pop() isn't really random!! Does that matter?
        all_rooms = set(room_dict.values())
        traversed_rooms = set()
        last_cohort = set()

        while all_rooms:
            next_room = all_rooms.pop()
            if last_cohort:
                logging.debug("adding a weird transition")
                next_room.add_exit(directions.purple, traversed_rooms.pop())
                last_cohort.clear()
            traversed_rooms.add(next_room)
            last_cohort.add(next_room)
            traversal_queue = collections.deque()
            traversal_queue.append(next_room)
            while traversal_queue:
                next_room = traversal_queue.popleft()
                actual_room = next_room

                for exit in actual_room.exits:
                    destination, _ = actual_room.exit(exit)
                    destination_number = destination
                    if destination_number in all_rooms:
                        all_rooms.remove(destination_number)
                        traversed_rooms.add(destination_number)
                        last_cohort.add(destination_number)
                        traversal_queue.append(destination_number)

        return Floor(room_dict)


# Manually generate the office so it is, tediously, always the same (and we also
# avoid the inappropriately exciting weird transitions).
# TODO: This is not in the spirit of roguelikes.
def _generate_office():
    desk = rooms._YourDesk()
    desk_coord = _Coordinate(10, 10)

    breakroom = rooms._BreakRoom()
    breakroom_coord = getattr(desk_coord, "east")
    _add_exit(desk, breakroom, "east")

    copier_room = rooms._CopierRoom()
    copier_room_coord = getattr(breakroom_coord, "north")
    _add_exit(breakroom, copier_room, "north")

    meeting_room = rooms._MeetingRoom()
    meeting_room_coord = getattr(desk_coord, "west")
    _add_exit(desk, meeting_room, "west")

    return Floor(
        {
            desk_coord: desk,
            breakroom_coord: breakroom,
            copier_room_coord: copier_room,
            meeting_room_coord: meeting_room,
        },
        {"DESK": desk},
    )
