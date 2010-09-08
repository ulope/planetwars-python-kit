# Copyright (c) 2010 Ulrich Petri <mail@ulo.pe>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from player import Player, Players, PLAYER1, PLAYER2, PLAYER3, PLAYER4, ME, NOBODY, ENEMIES, NOT_ME, EVERYBODY
from util import Point
from fleet import Fleet
from planet import Planet
from universe import Universe
from game import Game
from basebot import BaseBot

__doc__ = """planetwars

This is a Python "toolkit" for the second Google AI Contest (http://ai-constest.com).

Usage:
Create a class for your bot that inherits from BaseBot and implements a do_turn() method.
Then instantiate Game with your bot class as argument.

e.g.:

>>> from planetwars import BaseBot, Game
>>> from random import choice
>>>
>>> class MyBot(BaseBot):
...     def do_turn():
...         not_my_planets = list(self.universe.not_my_planets)
...         for planet in self.universe.my_planets:
...             planet.send_fleet(choice(not_my_planets), 5)
>>>
>>> Game(MyBot)
>>>
"""
