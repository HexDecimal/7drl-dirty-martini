

from __future__ import absolute_import, division, print_function
from builtins import *

from .base import MapGen
from . import rooms
from . import gateways

class TestGen(MapGen):
    def generate(self):
        self.width = 12
        self.height = 12
        self.depth = 4
        self.room_size = 8
        self.init(self.width * self.room_size,
                  self.height * self.room_size, self.depth)

        room = rooms.Outdoors(self, 0, 0, 0, self.room_size * self.width, self.room_size * self.height)
        room = rooms.Room(self, self.room_size * 2, self.room_size * 2, 0,
                                 self.room_size * 8, self.room_size * 4)
        room.subdivide_random(6, 4)
        room = rooms.Room(self, self.room_size * 6, self.room_size * 6, 0,
                                 self.room_size * 4, self.room_size * 4)
        room.subdivide_random(4, 4)

        for room in self.rooms:
            room.compile_neighbors()

        for room in self.rooms:
            for neighbor in room.neighbors:
                #if neighbor.connected:
                #    continue
                if neighbor in room.connected:
                    continue
                gateways.Doorway(self, room, neighbor)
                #break

        for gateway in self.gateways:
            gateway.generate()
        #for room in self.rooms:
        #    if not isinstance(room, rooms.Outdoors):
        #        continue
        #    print(room)
        #    for gateway in room.gateways:
        #        print(gateway)

