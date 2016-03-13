﻿

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

    def __init__(self, **kargs):
        pass

    def push(self, modal=False):
        assert self not in states
        states.append(self)
        if(modal):
            self.loop()

    def pop(self):
        assert self is states[-1]
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

    def key_down(self, event):
        print(event)

    def mouse_down(self, event):
        print(event)

    def mouse_motion(self, event):
        pass

    def get_index(self):
        return states.index(state)

    def draw(self, console):
        if self.get_index() != 0:
            states[self.get_index() - 1].draw(console)

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
        y = 0
        for i, item in enumerate(self.map.player.get_inventory(), 1):
            sideview.draw_str(1, y, '%i) %s' % (i, item.name))
            y += 1
            sideview.draw_str(1, y, item.desc_status())
            y += 1
            sideview.draw_rect(1, y, None, 1, '-')
            y += 1



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
        if event.char.upper() == 'S' or event.char.upper() == 'R':
            #new_map = map.Map(128,128,3)
            seed = 42
            if event.char.upper() == 'R':
                seed = random.randint(0, 1<<32-1)
                print('SEED %i' % seed)
            new_map = mapgen.generators.TestGen(seed).map
            player = actors.Actor(new_map[4,4,0], player=True)
            things.Pistol(player)
            things.Trackers(player, stock=10)
            MainGameState(new_map).push()
        super().key_down(event)

    def draw(self, console):
        console.clear()
        console.draw_str(2,2,'[S]tart')
        console.draw_str(3,3,'[R]andom')

def start():
    display.init()
    MainMenu().push(modal=True)
