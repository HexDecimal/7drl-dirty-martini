

from __future__ import absolute_import, division, print_function
from builtins import *

from things import GameObject

class Tile(GameObject):
    ch = '.'
    fg = 0x888888
    bg = 0x000000
    walkable = True
    transparent = True
    known_as_ch = ' '
    is_default = False
    is_tile = True

    def __init__(self):
        self.map = None
        self.x = self.y = self.z = None
        self.tracked = False
        self.objs = []
        
    def __repr__(self):
        return '<%s(x: %i, y: %i, z: %i)>' % (self.__class__.__name__,
                                              self.x, self.y, self.z)

    def is_visible(self):
        return self.tracked or self.map.tdl_data[self.z].fov[self.x, self.y]

    def is_known(self):
        return self.is_visible() or self.known_as_ch != ' '
        
    def get_cost(self, actor):
        return 100

    def get_graphic(self):
        if not self.is_visible():
            return self.known_as_ch, 0x444444, 0x000000
        ch, fg, bg = self.ch, self.fg, self.bg
        if self.objs:
            for obj in self.objs:
                ch, fg, bg = obj.get_graphic(ch, fg, bg)
        return ch, fg, bg

    def update_map_data(self):
        '''update walkable and transparency data

        call if walkable or transparent has changed'''
        self.map.tdl_data[self.z].walkable[self.x, self.y] = self.walkable
        self.map.tdl_data[self.z].transparent[self.x, self.y] = self.transparent
        self.map.trackers_dirty = True # will need to update trackers


    def ev_replacing(self, old_tile):
        self.objs.extend(old_tile.objs)
        for obj in old_tile.objs:
            if obj.loc is old_tile:
                obj.loc = self

    def ev_visible(self, actor):
        self.known_as_ch = self.ch

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
    WALL_CHARS = u'O│││─┘┐┤─└┌├─┴┬┼'.encode('cp437')
    walkable = False
    transparent = False

class Wall(Structure):
    def __init__(self):
        self.ch = None
        self.final_wall_type = None
        super().__init__()

    def get_wall_type_by_known(self):
        def is_known_structure(wall):
            return isinstance(wall, Structure) and wall.is_known()
        # UP, DOWN, LEFT, RIGHT
        wall_type = 1 * is_known_structure(self.map[self.x, self.y - 1, self.z])
        wall_type += 2 * is_known_structure(self.map[self.x, self.y + 1, self.z])
        wall_type += 4 * is_known_structure(self.map[self.x - 1, self.y, self.z])
        wall_type += 8 * is_known_structure(self.map[self.x + 1, self.y, self.z])
        return wall_type

    def get_final_wall_type(self):
        if self.final_wall_type is None:
            wall_type = 1 * isinstance(self.map[self.x, self.y - 1, self.z], Structure)
            wall_type += 2 * isinstance(self.map[self.x, self.y + 1, self.z], Structure)
            wall_type += 4 * isinstance(self.map[self.x - 1, self.y, self.z], Structure)
            wall_type += 8 * isinstance(self.map[self.x + 1, self.y, self.z], Structure)
            self.final_wall_type = wall_type
        return self.final_wall_type

    def get_graphic(self):
        #if self.final_wall_type is None:
        #    self.get_final_wall_type()
        #if self.ch != self.final_wall_type:
        #    self.ch = self.WALL_CHARS[self.get_wall_type_by_known()]
        if self.ch is None:
            self.ch = self.WALL_CHARS[self.get_final_wall_type()]
        return super().get_graphic()

class WoodenWall(Wall):
    pass


class Door(Structure):
    ch = '+'
    fg = 0x884400

    def __init__(self):
        super().__init__()
        self.opened = False

    def ev_bump(self, actor):
        self.ev_open(actor)

    def ev_open(self, actor):
        if self.opened:
            self.map.note('that\'s already open')
            return
        actor.time_used = 100
        self.ch = '.'
        self.walkable = self.transparent = self.opened = True
        self.update_map_data()
        
    def ev_close(self, actor):
        if not self.opened:
            self.map.note('that\'s already closed')
            return
        actor.time_used = 100
        self.ch = '+'
        self.walkable = self.transparent = self.opened = False
        self.update_map_data()
        

class Furniture(Tile):
    ch = '#'
    fg = 0x880000
    is_furniture = True

class PottedPlant(Furniture):
    ch = '*'
    fg = 0x008800
