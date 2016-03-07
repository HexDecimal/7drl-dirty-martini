

from __future__ import absolute_import, division, print_function
from builtins import *

import tiles
import sched

class Map(object):

    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.tiles = [None] * (width * height * depth)#[tiles.Tile(self) for _ in range(width * height * depth)]
        self.actors = []
        self.scheduler = sched.TickScheduler()
        self.camera_x = 0
        self.camera_y = 0
        self.camera_z = 0
        self.player = None
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    self[x,y,z] = tiles.Tile()

    def index(self, x, y, z):
        return x + y * self.width + z * self.width * self.height

    def __getitem__(self, xyz):
        return self.tiles[self.index(*xyz)]

    def __setitem__(self, xyz, tile):
        tile.x, tile.y, tile.z = xyz
        tile.map = self
        self.tiles[self.index(*xyz)] = tile
