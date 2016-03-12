

from __future__ import absolute_import, division, print_function
from builtins import *

class Tile(object):
    ch = '.'
    fg = 0x888888
    bg = 0x000000
    walkable = True
    transparent = True
    known_as_ch = ' '
    is_default = False

    def __init__(self):
        self.map = None
        self.x = self.y = self.z = None
        self.objs = []

    def is_visible(self):
        return self.map.tdl_data[self.z].fov[self.x, self.y]

    def get_graphic(self):
        if not self.is_visible():
            return self.known_as_ch, 0x444444, 0x000000
        ch, fg, bg = self.ch, self.fg, self.bg
        if self.objs:
            ch, fg = self.objs[-1].get_graphic()
        return ch, fg, bg

    def update_map_data(self):
        '''update walkable and transparency data

        call if walkable or transparent has changed'''
        self.map.tdl_data[self.z].walkable[self.x, self.y] = self.walkable
        self.map.tdl_data[self.z].transparent[self.x, self.y] = self.transparent


    def ev_replacing(self, old_tile):
        self.objs.extend(old_tile.objs)

    def ev_visible(self, actor):
        self.known_as_ch = self.ch

    def ev_bump(self, actor):
        pass

    def ev_open(self, actor):
        pass

    def ev_close(self, actor):
        pass

class Floor(Tile):
    'default floor'

class DefaultFloor(Floor):
    is_default = True

class DebugFloor(Floor):
    ch = '1'
    def ev_replacing(self, old_tile):
        super().ev_replacing(old_tile)
        if isinstance(old_tile, DebugFloor):
            self.ch = '%i' % min(9, int(old_tile.ch) + 1)

class GatewayDebugFloor(DebugFloor):
    fg = 0x444444

class Grass(Floor):
    ch = ','
    fg = 0x00cc22

class OpenSpace(Tile):
    'A apace with no wall or floor'
    ch = ' '
    bg = 0x00cccc

class DefaultOpenSpace(Floor):
    is_default = True

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

class Door(Structure):
    ch = '+'
    fg = 0x884400

    def __init__(self):
        super().__init__()
        self.opened = False

    def ev_bump(self, actor):
        self.ev_open(actor)

    def ev_open(self, actor):
        self.ch = '.'
        self.walkable = self.transparent = self.opened = True
        self.update_map_data()


