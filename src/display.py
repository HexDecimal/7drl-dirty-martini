

from __future__ import absolute_import, division, print_function
from builtins import *

import tdl

WIDTH = 80
HEIGHT = 60

console = None

def init():
    global console
    console = tdl.init(WIDTH, HEIGHT)