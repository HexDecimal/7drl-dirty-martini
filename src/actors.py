

from __future__ import absolute_import, division, print_function
from builtins import *

import states
import things

class Actor(things.Thing):
    ch = '@'

    def __init__(self, map, player=False, **kargs):
        map.actors.append(self)
        self.ticket = map.scheduler.schedule(0, self.ev_actor_ready)
        if player:
            map.player = self
        super().__init__(map=map, player=player, **kargs)

    def ev_actor_ready(self):
        'actor is ready to perform an action'
        if self.map.player is self:
            self.ev_player_ready()

    def ev_player_ready(self):
        for x, y in self.map.tdl_data[self.z].compute_fov(self.x, self.y,
                                                          'PERMISSIVE'):
            self.map[x, y, self.z].ev_visible(self)
        self.ticket = None # signal to the state that the player is idle

    def act_move(self, x, y, z=0):
        self.move_by(x, y, z)
        self.ticket = self.map.scheduler.schedule(100, self.ev_actor_ready)
