

from __future__ import absolute_import, division, print_function
from builtins import *

class Thing(object):
    ch = '?'
    fg = 0xffffff

    def __init__(self, map, x, y, z, **kargs):
        self.map = map
        self.x, self.y, self.z = x, y, z
        self.map[x,y,z].objs.append(self)

    def get_graphic(self):
        return self.ch, self.fg

    def can_move_to(self, x, y, z):
        return self.map[x,y,z].walkable

    def move_to(self, x, y, z=None):
        if z is None:
            z = self.z
        if not self.can_move_to(x, y, z):
            self.map[x,y,z].ev_bump(self)
            return
        self.map[self.x,self.y,self.z].objs.remove(self)
        self.map[x,y,z].objs.append(self)
        self.x, self.y, self.z = x, y, z

    def move_by(self, x, y, z=0):
        self.move_to(self.x + x, self.y + y, self.z + z)

