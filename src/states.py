﻿

from __future__ import absolute_import, division, print_function
from builtins import *

import tdl

import display
import tiles
import map
import mapgen
import things
import actors

states = []

class State(object):

    def __init__(self, **kargs):
        pass

    def push(self):
        assert self not in states
        states.append(self)

    def pop(self):
        assert self is states[-1]
        states.pop()

    def key_down(self, event):
        print(event)

    def mouse_down(self, event):
        print(event)

    def mouse_motion(self, event):
        pass

    def draw(self, console):
        pass

class MapState(State):
    padding_right = 20 # reserved space on side of console

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
        gameview = tdl.Window(console, 0, 0, -self.padding_right, None)
        sideview = tdl.Window(console, -self.padding_right, 0, None, None)
        cam_x, cam_y, cam_z = self.map.camera_center_on(self.map.player,
                                                        *gameview.get_size())
        for x,y in gameview:
            gameview.draw_char(x, y,
                              *self.map[x + cam_x, y + cam_y, cam_z]
                                                            .get_graphic())
        sideview.draw_rect(0, 0, 1, None, u'│'.encode('cp437'))

class MapEditor(MapState):
    pass

class MainGameState(MapState):

    Z_DIRS = {'<': 1, '>': -1}

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

    def key_down(self, event):
        if event.keychar in self.MOVE_DIRS:
            self.map.player.act_move(*self.MOVE_DIRS[event.keychar])
        if event.keychar in self.Z_DIRS:
            self.map.player.act_move(0, 0, self.Z_DIRS[event.keychar])
        self.simulate_until_player_is_ready()

class MainMenu(State):

    def key_down(self, event):
        if event.char.upper() == 'S':
            #new_map = map.Map(128,128,3)
            new_map = mapgen.generators.TestGen().map
            actors.Actor(map=new_map, x=4, y=4, z=0, player=True)
            MainGameState(new_map).push()
        super().key_down(event)

    def draw(self, console):
        console.clear()
        console.draw_str(2,2,'[S]tart')

def start():
    display.init()
    MainMenu().push()
    dirty = True
    while True:
        if not states:
            return

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
