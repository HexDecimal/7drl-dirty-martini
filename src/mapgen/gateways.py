

from __future__ import absolute_import, division, print_function
from builtins import *

import tiles

from .base import Gateway

class Doorway(Gateway):

    def post_adjustment(self):
        self.x = self.random.randint(self.x, self.x + self.width - 1)
        self.y = self.random.randint(self.y, self.y + self.height - 1)
        self.width = self.height = 1

    def generate(self):
        self.mapgen.map[self.x, self.y, self.z] = tiles.Door()
