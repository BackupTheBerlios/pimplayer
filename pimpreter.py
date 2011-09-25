# Pimp is a highly interactive music player.
# Copyright (C) 2011 kedals0@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Pimpreter permits to launch Pimp in python an intrepreter.
For example:
# python -i pimpreter.py
  Welcome on pimpreter
  ...
  >>> player.play()


"""
import atexit
import os
import readline
import rlcompleter
import sys

import pprint
sys.displayhook=lambda a : pprint.pprint(a)

# change autocomplete to tab
readline.parse_and_bind("tab: complete")

historyPath = os.path.expanduser("~/.pimpstory")

def save_history(historyPath=historyPath):
    import readline
    readline.write_history_file(historyPath)

if os.path.exists(historyPath):
    readline.read_history_file(historyPath)

atexit.register(save_history)

# Initialisation of Pimp
# ======================
import main
from pimp.extensions.tag import *
from pimp.extensions.context import *
from pimp.extensions.player_event import *
from pimp.core.song import *
from pimp.core.playlist import *
from pimp.core.db import File


print "Welcome on pimpreter"
print "--------------------"
print "Main object is player"
print ">>> player. and tab for completion on available method"
print "Some static class are also available:"
print "\tNote"
print "\tComment"
print "\t..."

from pimp.core.common import Info
# Redefining Info.__repr__() for a pretty print
def infoRepr(i):
    acc=""
    for (k,i) in i.items():
        acc=acc + k + ": " + str(i) + "\n"
    return acc
Info.__repr__=infoRepr


# anything not deleted (sys and os) will remain in the interpreter session
del atexit, readline, rlcompleter, save_history, historyPath, os, sys


