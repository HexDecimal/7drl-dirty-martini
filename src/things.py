

from __future__ import absolute_import, division, print_function
from builtins import *

class Thing(object):
    ch = '?'
    fg = 0xffffff

    def __init__(self, loc, **kargs):
        self.map = loc.map
        self.location = loc
        #self.x, self.y, self.z = x, y, z
        loc.objs.append(self)
        self.objs = []

    @property
    def x(self):
        return self.location.x
    @property
    def y(self):
        return self.location.y
    @property
    def z(self):
        return self.location.z


    def get_graphic(self):
        return self.ch, self.fg

    def can_move_by(self, x, y, z):
        return self.can_move_to(self.x + x,self.y + y,self.z + z)

    def can_move_to(self, x, y, z):
        return self.map[x,y,z].walkable

    def move_to(self, x, y, z=None):
        self.location.objs.remove(self)
        self.location = self.map[x,y,z]
        self.location.objs.append(self)

        #self.x, self.y, self.z = x, y, z
        return self.location.get_cost(self)

    def move_by(self, x, y, z=0):
        return self.move_to(self.x + x, self.y + y, self.z + z)

    def __repr__(self):
        return '<%s(location: %s)>' % (self.__class__.__name__, self.location)

class Loot(Thing):
    name = '[no name]'
    desc = '[I need a description]'
    
    def desc_status(self):
        return ''
        
class Equipment(Loot):
    ch = ']'
    stock = 1

    def __init__(self, loc, stock=None):
        super().__init__(loc)
        if stock is not None:
            self.stock = stock

class Pistol(Equipment):
    name = 'pistol'
    desc = ''
    stock = 15
    def desc_status(self):
        return '%6.i shots' % self.stock

class Trackers(Equipment):
    name = 'trackers'
    stock = 10
    
    def desc_status(self):
        return '%6.i left' % self.stock

