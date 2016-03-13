

from __future__ import absolute_import, division, print_function
from builtins import *

import textwrap

import tdl

import states
import tiles
import sched

class Map(object):

    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.tdl_data = [tdl.map.Map(width, height) for _ in range(depth)]
        self.tiles = [None] * (width * height * depth)#[tiles.Tile(self) for _ in range(width * height * depth)]
        self.actors = []
        self.log = []
        self.scheduler = sched.TickScheduler()
        self.player = None
        for z in range(self.depth):
            tile = tiles.DefaultFloor if z == 0 else tiles.DefaultOpenSpace
            for x in range(self.width):
                for y in range(self.height):
                    self[x,y,z] = tile()

    def camera_center_at(self, x, y, z, view_width, view_height):
        x = max(0, min(x - view_width // 2, self.width - view_width))
        y = max(0, min(y - view_height // 2, self.height - view_height))
        return x,y,z

    def camera_center_on(self, obj, view_width, view_height):
        return self.camera_center_at(obj.x, obj.y, obj.z,
                                     view_width, view_height)

    def note(self, msg):
        self.log += textwrap.wrap(msg, states.MapState.padding_right - 1)

    def index(self, x, y, z):
        return x + y * self.width + z * self.width * self.height

    def __getitem__(self, xyz):
        if(0 <= xyz[0] < self.width and 0 <= xyz[1] < self.height and
           0 <= xyz[2] < self.depth):
            return self.tiles[self.index(*xyz)]
        return tiles.Border()

    def __setitem__(self, xyz, tile):
        tile.x, tile.y, tile.z = xyz
        tile.map = self
        index = self.index(*xyz)
        old_tile = self.tiles[index]
        self.tiles[index] = tile
        tile.update_map_data()
        if old_tile is not None:
            tile.ev_replacing(old_tile)
