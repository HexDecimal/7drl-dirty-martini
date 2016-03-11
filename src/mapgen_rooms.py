

from __future__ import absolute_import, division, print_function
from builtins import *

import mapgen
import tiles

class Outdoors(mapgen.Room):
    def generate(self):
        for pos in self.get_inner():
            if self.mapgen.map[pos].is_default:
                self.mapgen.map[pos] = tiles.Grass()
        for pos in self.get_walls():
            if self.mapgen.map[pos].is_default:
                self.mapgen.map[pos] = tiles.Grass()