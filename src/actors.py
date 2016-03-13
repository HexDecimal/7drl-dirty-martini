

from __future__ import absolute_import, division, print_function
from builtins import *

import states
import things

class Actor(things.Thing):
    ch = '@'

    def __init__(self, loc, player=False, **kargs):
        super().__init__(loc, player=player, **kargs)
        self.map.actors.append(self)
        self.ticket = self.map.scheduler.schedule(0, self.ev_actor_ready)
        if player:
            self.map.player = self

    def ev_actor_ready(self):
        'actor is ready to perform an action'
        if self.map.player is self:
            self.ev_player_ready()

    def ev_player_ready(self):
        for x, y in self.map.tdl_data[self.z].compute_fov(self.x, self.y,
                                                 'PERMISSIVE', 50):
            self.map[x, y, self.z].ev_visible(self)
        self.ticket = None # signal to the state that the player is idle

    def bump(self, x, y, z=0):
        self.map[self.x + x, self.y + y, self.z + z].ev_bump(self)

    def act_move(self, x, y, z=0):
        self.time_used = 0
        if self.can_move_by(x, y, z):
            self.time_used += self.move_by(x, y, z)
        else:
            self.bump(x, y, z)
        self.ticket = self.map.scheduler.schedule(self.time_used, self.ev_actor_ready)

    def act_pickup(self):
        self.map.note('nothing to pickup')

    def act_drop(self):
        self.map.note('nothing can be dropped')

    def act_examine(self):
        self.map.note('not implemented')

    def get_inventory(self):
        for obj in self.objs:
            if isinstance(obj, things.Loot):
                yield obj
