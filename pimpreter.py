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

atexit.register(main.quit)


# anything not deleted (sys and os) will remain in the interpreter session
del atexit, readline, rlcompleter, save_history, historyPath, os, sys


