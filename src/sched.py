#!/usr/bin/env python
"""
    sched.py - a small tick-based scheduler for game development

    Written in 2016 by Kyle Stewart 4b796c65+sched@gmail.com

    To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.

    You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
"""

import heapq as _heapq

class TickScheduler(object):

    class Ticket(object):

        def __init__(self, func, *args, **kargs):
            self.tick = None
            self.id = None
            self.func = func
            self.args = args
            self.kargs = kargs
            self.canceled = False

        def __lt__(self, other):
            return ((self.tick == other.tick and self.id < other.id)
                    or self.tick < other.tick)

        def __repr__(self):
            return '<Ticket for %i, (%r, *%r, **%r)>' % (self.tick,
                self.func, self.args, self.kargs)

    def __init__(self):
        self.tick = 0 # current "time"
        self._next_entry_id = 0 # tie-breaker to enforce FIFO of tickets
        self._pqueue = [] # priority queue of events maintained by heapq

    def schedule(self, interval, func, *args, **kargs):
        """Schedule a call to func(*args, **kargs) after interval ticks.

        interval must be an integer.
        """
        interval = int(interval) # prevent loss of precision by enforcing int
        ticket = self.Ticket(func, *args, **kargs)
        ticket.tick = self.tick + interval
        ticket.id = self._next_entry_id
        self._next_entry_id += 1 # increment infinitely / sort FIFO
        _heapq.heappush(self._pqueue, ticket)
        return ticket

    def next(self):
        """Runs the next scheduled call"""
        assert self._pqueue, 'event queue is empty'
        ticket = _heapq.heappop(self._pqueue)
        self.tick = ticket.tick
        if ticket.canceled:
            return
        ticket.func(*ticket.args, **ticket.kargs) # actually call the event

    def __repr__(self):
        """A fancy string representation that lists current time and number of
        tickets."""
        return ('<%s on tick %i with %i tickets>' %
                (self.__class__.__name__, self.tick,
                 len(self._pqueue)))
