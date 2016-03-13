

from __future__ import absolute_import, division, print_function
from builtins import *

import random

import tdl

import display
import tiles
import map
import mapgen
import things
import actors

states = []

class State(object):

    ACTIONS = {'G': 'pickup',
               'D': 'drop',
               'X': 'examine',
               'A': 'apply',
               'C': 'close',
               'O': 'open',}

    Z_DIRS = {'<': 1, '>': -1}

    DIRS = ((-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            )
    
    MOVE_DIRS = {'LEFT': (-1, 0),
              'RIGHT': (1, 0),
              'UP': (0, -1),
              'DOWN': (0, 1),
              'KP1': (-1, 1),
              'KP2': (0, 1),
              'KP3': (1, 1),
              'KP4': (-1, 0),
              'KP5': (0, 0),
              'KP6': (1, 0),
              'KP7': (-1, -1),
              'KP8': (0, -1),
              'KP9': (1, -1),}

    def __init__(self, **kargs):
        pass

    def push(self, modal=False):
        assert self not in states
        states.append(self)
        self.enter()
        if(modal):
            self.loop()
        return self

    def pop(self):
        assert self is states[-1]
        self.exit()
        states.pop()

    def loop(self):
        dirty = True
        while self in states:
            if dirty:
                states[-1].draw(display.console)
                tdl.flush()
                dirty = False
            event = tdl.event.wait(flush=False)
            if event.type == 'QUIT':
                return
            elif event.type == 'KEYDOWN':
                dirty = True
                states[-1].key_down(event)
            elif event.type == 'MOUSEDOWN':
                dirty = True
                states[-1].mouse_down(event)
            elif event.type == 'MOUSEMOTION':
                dirty = True
                states[-1].mouse_motion(event)

    def enter(self):
        pass

    def exit(self):
        pass

    def key_down(self, event):
        print(event)

    def mouse_down(self, event):
        print(event)

    def mouse_motion(self, event):
        pass

    def get_index(self):
        return states.index(self)

    def next_state(self):
        index = states.index(self)
        return None if index == 0 else states[index - 1]

    def __getattr__(self, attr):
        if self not in states:
            raise AttributeError(attr)
        next = self.next_state()
        if next is None:
            raise AttributeError(attr)
        return getattr(next, attr)

    def draw(self, console):
        if self.get_index() != 0:
            states[self.get_index() - 1].draw(console)

class MapState(State):
    padding_right = 24 # reserved space on side of console

    def __init__(self, map, **kargs):
        self.map = map
        super().__init__(map=map, **kargs)
        self.simulate_until_player_is_ready()

    def simulate_until_player_is_ready(self):
        while self.map.player.ticket is not None:
            self.map.scheduler.next()
        #print(self.map.scheduler)

    def draw(self, console):
        #console.clear()
        self.map.refresh()
        gameview = tdl.Window(console, 0, 0, -self.padding_right, None)
        sideview = tdl.Window(console, -self.padding_right, 0, None, None)
        cam_x, cam_y, cam_z = self.map.camera_center_on(self.map.player,
                                                        *gameview.get_size())
        for x,y in gameview:
            gameview.draw_char(x, y,
                              *self.map[x + cam_x, y + cam_y, cam_z]
                                                            .get_graphic())
        sideview.clear()
        sideview.draw_rect(0, 0, 1, None, u'│'.encode('cp437'))
        y = 0
        for item in sorted(self.map.player.get_inventory(), key=lambda o:o.key):
            sideview.draw_str(1, y, '%s) %s' % (item.key, item.name))
            y += 1
            sideview.draw_str(1, y, item.desc_status())
            y += 1
            sideview.draw_rect(1, y, None, 1, '-')
            y += 1
        height = console.height - y
        for i, line in enumerate(reversed(self.map.log[-height:]), 1):
            sideview.draw_str(1, -i, line)



class MapEditor(MapState):
    pass

class MainGameState(MapState):

    def key_down(self, event):
        key = event.keychar.upper()
        if key in self.MOVE_DIRS:
            self.map.player.act_move(*self.MOVE_DIRS[event.keychar])
        elif key in self.Z_DIRS:
            self.map.player.act_move(0, 0, self.Z_DIRS[event.keychar])
        elif key in self.ACTIONS:
            getattr(self.map.player, 'act_%s' % self.ACTIONS[key])()
        elif self.map.player.get_item_by_assignment(key):
            self.map.player.act_apply(self.map.player.get_item_by_assignment(key))
        self.simulate_until_player_is_ready()

class ModalState(State):
    pass

class ModalAskWhichItem(ModalState):
    def __init__(self, msg):
        self.msg = msg
        self.item = None

    def enter(self):
        self.map.note(self.msg)

    def key_down(self, event):
        key = event.keychar.upper()
        self.item = self.map.player.get_item_by_assignment(key)
        self.pop()

class ModalUseWhere(ModalState):
    def __init__(self, msg):
        self.msg = msg
        self.temp_objs = []
        self.dir = None
        
    def enter(self):
        self.temp_objs = [things.Highlight(self.map.player.get_relative_tile(x, y))
                          for x, y in self.DIRS]
        self.map.note(self.msg)
        
    def exit(self):
        for obj in self.temp_objs:
            obj.remove()

    def key_down(self, event):
        key = event.keychar.upper()
        if key in self.MOVE_DIRS:
            self.dir = self.MOVE_DIRS[key]
        self.pop()

class MainMenu(State):

    def key_down(self, event):
        if event.char.upper() == 'S' or event.char.upper() == 'R':
            #new_map = map.Map(128,128,3)
            seed = 42
            if event.char.upper() == 'R':
                seed = random.randint(0, 1<<32-1)
                print('SEED %i' % seed)
            new_map = mapgen.generators.TestGen(seed).map
            player = actors.Actor(new_map[4,4,0], player=True)
            things.Pistol(player)
            things.Trackers(player)
            MainGameState(new_map).push()
        super().key_down(event)

    def draw(self, console):
        console.clear()
        console.draw_str(2,2,'[S]tart')
        console.draw_str(3,3,'[R]andom')

def start():
    display.init()
    MainMenu().push(modal=True)
