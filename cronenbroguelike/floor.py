import collections
import logging
import random

from cronenbroguelike import rooms
from engine import dice
from engine import directions


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
    def __init__(self, room_dict):
        self._rooms = room_dict

    def __getitem__(self, coordinate):
        return self._rooms[coordinate]

    def random_room(self):
        return random.choice(list(self._rooms.values()))

    @classmethod
    def generate(cls, theme, number_rooms):
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
            coordinate = coordinate_queue.popleft()
            if room_dict.get(coordinate) is not None:
                continue

            # Creates a new room in that location.
            room_dict[coordinate] = room

            for direction in ["north", "south", "east", "west"]:
                # Adds some exits.
                new_coordinate = getattr(coordinate, direction)
                next_room = room_dict.get(new_coordinate)
                if next_room is not None:
                    if dice.roll("1d100") > 50:
                        _add_exit(room, next_room, direction)

                # Randomly decides where else to add rooms.
                if dice.roll("1d100") > 25:
                    coordinate_queue.append(new_coordinate)

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
