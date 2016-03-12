#!/usr/bin/env python2

from __future__ import absolute_import, division, print_function
from builtins import * # 'future' module

import sys

import logging

import states

if __name__ == '__main__':
    if '-v' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    states.start()
