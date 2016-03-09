

from __future__ import absolute_import, division, print_function
from builtins import *

class Tile(object):
    ch = '.'
    fg = 0x888888
    bg = 0x000000
    walkable = True
    transparent = True

    def __init__(self):
        self.map = None
        self.x = self.y = self.z = None
        self.objs = []

    def get_graphic(self):
        ch, fg, bg = self.ch, self.fg, self.bg
        if self.objs:
            ch, fg = self.objs[-1].get_graphic()
        return ch, fg, bg

class Floor(Tile):
    'default floor'

class OpenSpace(Tile):
    'A apace with no wall or floor'
    ch = ' '
    bg = 0x00cccc

class Border(Tile):
    ch = '!'
    walkable = False

class Structure(Tile):
    ch = '#'
    walkable = False
    transparent = False

    def __init__(self):
        #self.ch = None
        super().__init__()

    def get_graphic(self):
        if self.ch is None:
            pass
        return super().get_graphic()

class WoodenWall(Structure):
    pass

class Wall(WoodenWall):
    'default wall'
