

from __future__ import absolute_import, division, print_function
from builtins import *

class Tile(object):
    ch = '.'
    fg = 0x888888
    bg = 0x000000
    def __init__(self):
        self.map = None
        self.x = self.y = self.z = None
        self.objs = []

    def get_graphic(self):
        ch, fg, bg = self.ch, self.fg, self.bg
        if self.objs:
            ch, fg = self.objs[-1].get_graphic()
        return ch, fg, bg
