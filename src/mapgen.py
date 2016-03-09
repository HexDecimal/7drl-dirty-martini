

from __future__ import absolute_import, division, print_function
from builtins import *

import random

import map
import tiles

class Zone(object):

    def __init__(self, mapgen):
        self.mapgen = mapgen
        self.zone = set()

    def add_rect(self, x, y, z, width, height, depth):
        for z_ in range(z, z + depth):
            for y_ in range(y, y + height):
                for x_ in range(x, x + width):
                    self.zone.add((x_, y_, z_))

    def add_layer(self, z):
        self.add_rect(0, 0, z, self.mapgen.width, self.mapgen.height, 1)

    def add_all(self):
        self.add_rect(0, 0, 0, self.mapgen.width, self.mapgen.height, self.mapgen.depth)

class Gateway(object):
    def __init__(self, mapgen, x, y, z, width, height):
        self.mapgen = mapgen
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height

    def in_bounds(self, x, y, z=None):
        return (self.x <= x < self.x + width and self.y <= y < self.y + height
                and (z is None or z == self.z))

class Room(object):

    def __init__(self, mapgen, x, y, z, width, height):
        self.mapgen = mapgen
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.neighbors = []
        self.gateways = []

    @property
    def x2(self):
        return self.x + self.width

    @property
    def y2(self):
        return self.y + self.height

    #@property
    #def z2(self):
    #    return self.z + self.depth


    def get_intersection(self, other):
        def range_intersection(self, x1, width1, x2, width2):
            if x2 < x1:
                x1, x2, width1, width2 = x2, x1, width2, width1
            return x1, x1 + width1 - x2

        if (self.z != other.z or
            self.x2 < other.x or
            self.y2 < other.y or
            self.x > other.x2 or
            self.y > other.y2):
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

        if intersect_x is not None:
            y, height = range_intersection(self.y, self.height,
                                           other.y, other.height)
            if h > 2:
                return (intersect_x, y, 1, height)
        if intersect_y is not None:
            x, width = range_intersection(self.x, self.width,
                                          other.x, other.width)
            if w > 2:
                return (x, intersect_y, width, 1)
        return None

    def compile_neighbors(self):
        self.neighbors = [room for room in self.mapgen.rooms
                          if self.get_intersection(room)]

    def get_inner(self):
        for y in range(1, self.height):
            for x in range(1, self.width):
                yield x,y,self.z

    def get_outer(self):
        for x in range(self.x, self.x + self.width + 1):
            yield x, self.y, self.z
            yield x, self.y + self.height, self.z
        for y in range(self.y + 1, self.y + self.height):
            yield self.x, y, self.z
            yield self.x + self.width, y, self.z

    def generate(self):
        for pos in self.get_inner():
            self.mapgen.map[pos] = tiles.Floor()
        for pos in self.get_outer():
            self.mapgen.map[pos] = tiles.Wall()



class MapGen(object):

    def __init__(self):
        self.width = 8
        self.height = 8
        self.depth = 4
        self.room_size = 8
        self.rooms = []
        #self.tiles_touched = set()
        self.map = map.Map(self.width * self.room_size + 1,
                           self.height * self.room_size + 1, self.depth)
        #self.zones = [Zone(self)]
        #self.zones[0].add_all()
        for x in range(self.width):
            for y in range(self.height):
                self.rooms.append(
                    Room(self, x * self.room_size, y * self.room_size, 0,
                         self.room_size, self.room_size))
        for room in self.rooms:
            room.generate()

    def in_bounds(self, x, y, z):
        return (0 <= x < self.width and 0 <= y < self.height and
                0 <= z < self.depth)


