

from __future__ import absolute_import, division, print_function
from builtins import *

import states
import things

def action_func(func):
    def new_func(self, *args, **kargs):
        self.time_used = 0
        func(self, *args, **kargs)
        self.ticket = self.map.scheduler.schedule(self.time_used, self.ev_actor_ready)
    return new_func

class Actor(things.Thing):
    ch = '@'
    is_actor = True

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
        self.ticket = None # signal to the state that the player is idle

    def bump(self, x, y, z=0):
        self.map[self.x + x, self.y + y, self.z + z].ev_bump(self)

    def get_item_by_assignment(self, key):
        for obj in self.objs:
            if obj.key == key:
                return obj
        return None

    def get_next_item_key(self):
        for key in '123456789abcdefghijklmnopqrstuvwxyz'.upper():
            if self.get_item_by_assignment(key) is None:
                return key
        assert False, 'way too many objects picked up'
        return '0'

    @action_func
    def act_move(self, x, y, z=0):
        self.time_used = 0
        if self.can_move_by(x, y, z):
            self.time_used += self.move_by(x, y, z)
        else:
            self.bump(x, y, z)
        self.ticket = self.map.scheduler.schedule(self.time_used, self.ev_actor_ready)

    @action_func
    def act_pickup(self):
        self.time_used = 0
        for obj in list(self.location.objs):
            if isinstance(obj, things.Loot):
                obj.move_to(self)
                self.map.note('you take the %s' % obj.name)
                break
        else:
            self.map.note('nothing here to pickup')
            return
        for obj in list(self.location.objs):
            if isinstance(obj, things.Loot):
                self.map.note('there\'s still stuff here')
                break

    def ask_player_for_item(self, item, msg):
        if item is not None:
            return item
        return states.ModalAskWhichItem(msg).push(True).item

    def ask_player_for_dir(self, msg):
        return states.ModalUseWhere(msg).push(True).dir

    @action_func
    def act_drop(self, item=None):
        item = self.ask_player_for_item(item, 'which item should be dropped?')
        if item is None:
            self.map.note('nevermind')
            return
        self.time_used += 50
        item.move_to(self.location)
        self.map.note('you drop the %s' % item.name)

    @action_func
    def act_apply(self, item=None):
        item = self.ask_player_for_item(item, 'use which item?')
        if item is None:
            self.map.note('nevermind')
            return
        item.use_item(self)

    @action_func
    def act_examine(self):
        self.map.note('not implemented')

    @action_func
    def act_open(self):
        dir = self.ask_player_for_dir('open what?')
        if dir is None:
            self.map.note('nevermind')
        tile = self.get_relative_tile(*dir)
        tile.ev_open(self)

    @action_func
    def act_close(self):
        dir = self.ask_player_for_dir('close what?')
        if dir is None:
            self.map.note('nevermind')
        tile = self.get_relative_tile(*dir)
        tile.ev_close(self)

    def get_inventory(self):
        for obj in self.objs:
            if isinstance(obj, things.Loot):
                yield obj
