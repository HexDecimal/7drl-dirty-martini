

from __future__ import absolute_import, division, print_function
from builtins import *

class GameObject(object):
    ch = '?'
    fg = 0xffffff
    key = None
    is_actor = False
    is_furniture = False
    is_tile = False
    can_pickup = False

    def is_player(self):
        return self.map.player is self

    def get_relative_tile(self, x, y, z=0):
        return self.map[self.x + x, self.y + y, self.z + z]

    def get_cost(self, actor):
        return 0

    def ev_open(self, actor):
        self.map.note('you can\'t open that')

    def ev_close(self, actor):
        self.map.note('you can\'t close that')

    def ev_bump(self, actor):
        pass

    def ev_added(self):
        pass

    def ev_removing(self):
        pass
        
    def ev_pickup(self, actor):
        pass


class Thing(GameObject):
    ch = '?'
    fg = 0xffffff

    def __init__(self, loc, **kargs):
        self.map = loc.map
        self.location = loc
        loc.objs.append(self)
        self.objs = []
        self.ev_added()

    @property
    def x(self):
        return self.location.x
    @property
    def y(self):
        return self.location.y
    @property
    def z(self):
        return self.location.z

    def remove(self):
        self.move_to(None)

    def get_graphic(self, ch, fg, bg):
        return self.ch, self.fg, bg

    def can_move_by(self, x, y, z):
        return self.can_move_to(self.x + x,self.y + y,self.z + z)

    def can_move_to(self, x, y, z):
        return self.map[x,y,z].walkable

    def move_to(self, new_loc):
        if self.location is not None:
            self.ev_removing()
            self.location.objs.remove(self)
        self.location = new_loc
        if new_loc is not None:
            new_loc.objs.append(self)
            self.ev_added()
            return new_loc.get_cost(self)
        return 0

    def move_by(self, x, y, z=0):
        return self.move_to(self.map[self.x + x, self.y + y, self.z + z])

    def __repr__(self):
        return '<%s(location: %s)>' % (self.__class__.__name__, self.location)

class Highlight(Thing):
    def get_graphic(self, ch, fg, bg):
        return ch, fg, 0xffffff

class Loot(Thing):
    name = '[no name]'
    desc = '[I need a description]'
    can_pickup = True

    def __init__(self, loc):
        self.key = None
        super().__init__(loc)

    def ev_added(self):
        if self.location.is_player():
            self.key = None
            self.key = self.location.get_next_item_key()

    def ev_pickup(self, actor):
        self.move_to(actor)
        self.map.note('you take the %s' % self.name)
            
    def use_item(self, actor):
        self.map.note('no action for your %s' % self.name)
        return 0

    def desc_status(self):
        return ''

class Equipment(Loot):
    ch = ']'
    charges = 1

    def __init__(self, loc, charges=None):
        super().__init__(loc)
        if charges is not None:
            self.charges = charges

class Pistol(Equipment):
    name = 'pistol'
    desc = ''
    charges = 15
    def desc_status(self):
        return '%6.i shots' % self.charges

class Trackers(Equipment):
    name = 'bugs'
    charges = 10

    def use_item(self, actor):
        dir = actor.ask_player_for_dir('pick a direction to place bug')
        if dir is None:
            self.map.note('nevermind')
        tile = self.get_relative_tile(*dir)
        if tile.is_furniture:
            TrackersActive(tile)
            self.charges -= 1
            if self.charges == 0:
                self.remove()
            self.map.note('done')
            return
        #self.map.note('must be placed on furniture/npcs')
        self.map.note('must be placed on furniture')

    def desc_status(self):
        return '%6.i left' % self.charges

class TrackersActive(Trackers):
    charges = 1

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.map.trackers_dirty = True
        self.map.trackers.append(self)

    def ev_removing(self):
        self.map.trackers_dirty = True
        self.map.trackers.remove(self)

    def ev_pickup(self, actor):
        self.remove()
        for obj in actor.objs:
            if isinstance(obj, Trackers):
                obj.charges += 1
                break
        else:
            Trackers(actor, charges=1)
        self.map.note('you take the %s' % self.name)
        
    def get_graphic(self, ch, fg, bg):
        return ch, 0xffffff, bg
