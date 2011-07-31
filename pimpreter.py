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

# change autocomplete to tab
readline.parse_and_bind("tab: complete")

historyPath = os.path.expanduser("~/.pimpstory")

def save_history(historyPath=historyPath):
    import readline
    readline.write_history_file(historyPath)

if os.path.exists(historyPath):
    readline.read_history_file(historyPath)

atexit.register(save_history)

import main
from pimp.core.tag import *
from pimp import *

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

# def listRepr(l):
#     acc=""
#     for l in i:
#         acc=acc + str(i) + "\n"
#     return acc

# list.__repr__=listRepr
    

atexit.register(quit)

# anything not deleted (sys and os) will remain in the interpreter session
del atexit, readline, rlcompleter, save_history, historyPath, os, sys


