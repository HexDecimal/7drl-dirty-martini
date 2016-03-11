

from __future__ import absolute_import, division, print_function
from builtins import *

import logging
import random as _random

import map
import tiles

class RoomGenerationException(Exception):
    pass

class RoomSplitException(RoomGenerationException):
    pass

def range_intersection(x1, width1, x2, width2):
    return max(x1, x2), min(x1 + width1 - x2, x2 + width2 - x1,
                            width1, width2)

class Gateway(object):
    def __init__(self, mapgen, room1, room2):
        for gate in room1.gateways:
            if gate in room2.gateways:
                raise RoomGenerationException(
                    'rooms already share an existing gateway')
        self.mapgen = mapgen

        intersect = room1.get_intersection(room2)
        if not intersect:
            raise RoomGenerationException('can not connect %s to %s' %
                                          (room1, room2))
        self.x, self.y, self.z, self.width, self.height = intersect

        room1.connected.append(room2)
        room2.connected.append(room1)
        room1.gateways.append(self)
        room2.gateways.append(self)

        self.rooms = (room1, room2)
        self.mapgen.gateways.append(self)

        self.post_adjustment()

        logging.debug('new %s', self)

    def post_adjustment(self):
        pass

    def in_bounds(self, x, y, z=None):
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height and
                (z is None or z == self.z))

    def get_inner(self):
        for x in range(self.x, self.x + self.width):
            for y in range(self.y, self.y + self.height):
                yield x, y, self.z

    def generate(self):
        for pos in self.get_inner():
            self.mapgen.map[pos] = tiles.GatewayDebugFloor()

    def __repr__(self):
        return ('<%s(X:%i, Y:%i, Z:%i, Width:%i, Height:%i)>' %
                (self.__class__.__name__,
                 self.x, self.y, self.z, self.width, self.height))

class Room(object):

    def __init__(self, mapgen, x, y, z, width, height, auto_cull=True):
        self.mapgen = mapgen
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.neighbors = []
        self.connected = []
        self.gateways = []
        if auto_cull:
            for room in self.mapgen.rooms:
                room.cull_rect(self.x, self.y, self.z, self.width, self.height)
        self.mapgen.rooms.append(self)

    @property
    def alive(self):
        return self.mapgen is not None

    @property
    def x2(self):
        return self.x + self.width

    @property
    def y2(self):
        return self.y + self.height

    @property
    def random(self):
        return self.mapgen.random

    def is_empty(self):
        return self.width == 0 or self.height == 0

    def in_bounds(self, x, y, z=None):
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height and
                (z is None or z == self.z))

    def is_inside_rect(self, x, y, width, height):
        return(x <= self.x and self.x + self.width <= x + width and
               y <= self.y and self.y + self.height <= y + height)

    def get_intersection(self, other):
        if (self.z != other.z or
            self.x2 < other.x or self.y2 < other.y or
            self.x > other.x2 or self.y > other.y2):
            return None

        intersect_x = None
        intersect_y = None
        if self.x == other.x2:
            intersect_x = self.x
        elif other.x == self.x2:
            intersect_x = other.x
        if self.y == other.y2:
            intersect_y = self.y
        elif other.y == self.y2:
            intersect_y = other.y

        intersection = None
        if intersect_x is not None:
            y, height = range_intersection(self.y, self.height,
                                           other.y, other.height)
            if height >= 2:
                y += 1
                height -= 1
                intersection = (intersect_x, y, self.z, 1, height)
        if intersect_y is not None:
            x, width = range_intersection(self.x, self.width,
                                          other.x, other.width)
            if width >= 2:
                x += 1
                width -= 1
                intersection = (x, intersect_y, self.z, width, 1)
        if intersection:
            logging.debug('%s %s %s', self, other, intersection)
        return intersection

    def delete(self):
        assert self.mapgen is not None, 'already removed'
        self.mapgen.rooms.remove(self)
        self.mapgen = None
        self.width = self.height = 0

    def can_merge_with(self, other):
        'by default, this can merge with other rooms of the same class'
        return self.__class__ == other.__class__

    def auto_merge_with(self, other):
        assert self.alive
        assert other.alive
        if self is other:
            return False
        if not self.can_merge_with(other):
            return False
        if(self.y == other.y and self.height == other.height and
           (self.x + self.width == other.x or other.x + other.width == self.x)):
           self.x = min(self.x, other.x)
           self.width += other.width
           other.delete()
           return True
        if(self.x == other.x and self.width == other.width and
           (self.y + self.height == other.y or other.y + other.height == self.y)):
           self.y = min(self.y, other.y)
           self.height += other.height
           other.delete()
           return True
        return False

    def cull_rect(self, x, y, z, width, height):
        if self.z != z:
            return
        rooms = [self]
        for room in list(rooms):
            try:
                rooms.append(room.split_global_x(x)[1])
            except RoomSplitException:
                pass
        for room in list(rooms):
            try:
                rooms.append(room.split_global_x(x + width)[1])
            except RoomSplitException:
                pass
        for room in list(rooms):
            try:
                rooms.append(room.split_global_y(y)[1])
            except RoomSplitException:
                pass
        for room in list(rooms):
            try:
                rooms.append(room.split_global_y(y + height)[1])
            except RoomSplitException:
                pass

        self.random.shuffle(rooms)

        for room in list(rooms):
            if room.is_inside_rect(x, y, width, height):
                room.delete()
                rooms.remove(room)
                break

        for i, room in enumerate(rooms):
            if not room.alive:
                continue
            continue_merge = True
            while continue_merge:
                continue_merge = False
                for other_room in rooms[i+1:]:
                    if not other_room.alive:
                        continue
                    if room.auto_merge_with(other_room):
                        continue_merge = True

    def split_local_x(self, x):
        if not (0 <= x < self.width):
            raise RoomSplitException('value is out of bounds')
        if x == 0 or x == self.width:
            raise RoomSplitException('this would create an empty room')
        new_room = self.__class__(self.mapgen, self.x + x, self.y, self.z,
                                  self.width - x, self.height, auto_cull=False)
        self.width = x
        return self, new_room # return left_room, right_room

    def split_global_x(self, x):
        'split a room along a global value of x'
        return self.split_local_x(x - self.x)

    def split_local_y(self, y):
        if not (0 <= y < self.height):
            raise RoomSplitException('value is out of bounds')
        if y == 0 or y == self.height:
            raise RoomSplitException('this would create an empty room')
        new_room = self.__class__(self.mapgen, self.x, self.y + y, self.z,
                                  self.width, self.height - y, auto_cull=False)
        self.height = y
        return self, new_room

    def split_global_y(self, y):
        return self.split_local_y(y - self.y)

    def split_global_xy(self, x, y):
        top, bottom = self.split_global_y(y)
        top_left, top_right = top.split_on_x(x)
        bottom_left, bottom_right = bottom.split_global_x(x)
        return top_left, top_right, bottom_left, bottom_right

    def compile_neighbors(self):
        self.neighbors = [room for room in self.mapgen.rooms
                          if self.get_intersection(room)]

    def get_inner(self):
        for x in range(self.x, self.x + self.width):
            for y in range(self.y, self.y + self.height):
                yield x, y, self.z

    def get_floors(self):
        for x in range(self.x + 1, self.x + self.width):
            for y in range(self.y + 1, self.y + self.height):
                yield x, y, self.z

    def get_outer(self):
        for x in range(self.x, self.x + self.width + 1):
            yield x, self.y, self.z
            yield x, self.y + self.height, self.z
        for y in range(self.y + 1, self.y + self.height):
            yield self.x, y, self.z
            yield self.x + self.width, y, self.z

    def get_walls(self):
        for x, y, z in self.get_outer():
            for gateway in self.gateways:
                if gateway.in_bounds(x, y):
                    break
            else:
                yield x, y, z

    def subdivide_x(self, min_size):
        if self.width < min_size * 2:
            return [self]
        return self.split_local_x(self.random.randint(min_size, self.width - min_size))

    def subdivide_y(self, min_size):
        if self.height < min_size * 2:
            return [self]
        return self.split_local_y(self.random.randint(min_size, self.height - min_size))

    def subdivide_random(self, iterations=1, min_size=3):
        logging.debug('subdividing room %s', self)
        rooms = [self]
        can_divide_x = self.width >= min_size * 2
        can_divide_y = self.height >= min_size * 2
        if not (can_divide_x or can_divide_y):
            logging.debug('room not big enough to subdivide')
            return rooms
        if can_divide_x and not can_divide_y:
            if can_divide_x:
                rooms = self.subdivide_x(min_size)
            else:
                rooms = self.subdivide_y(min_size)
        elif self.random.uniform(0, self.width + self.height) < self.width:
            rooms = self.subdivide_x(min_size)
        else:
            rooms = self.subdivide_y(min_size)
        iterations -= 1
        rooms = list(rooms)
        if(iterations > 0):
            for room in list(rooms):
                rooms += room.subdivide_random(iterations, min_size)[1:]
        return rooms

    def generate(self):
        for pos in self.get_floors():
            self.mapgen.map[pos] = tiles.Floor()
        for pos in self.get_walls():
            self.mapgen.map[pos] = tiles.Wall()

    def __repr__(self):
        return ('<%s(X:%i, Y:%i, Width:%i, Height:%i)>' %
            (self.__class__.__name__, self.x, self.y, self.width, self.height))


class MapGen(object):

    def __init__(self):
        self.generate()
        #print(self.rooms)
        for room in self.rooms:
            print(room)
            room.generate()

    def generate(self):
        self.width = 8
        self.height = 8
        self.depth = 4
        self.room_size = 8
        self.init(self.width * self.room_size,
                  self.height * self.room_size, self.depth)

        room = Room(self, 0, 0, 0, self.room_size * 8, self.room_size * 8)
        Room(self, self.room_size * 2, self.room_size * 2, 0,
                   self.room_size * 2, self.room_size * 2)

    def init(self, width, height, depth):
        self.random = _random.Random(42)
        self.rooms = []
        self.gateways = []
        self.map = map.Map(width + 1, height + 1, depth)


    def in_bounds(self, x, y, z):
        return (0 <= x < self.width and 0 <= y < self.height and
                0 <= z < self.depth)


