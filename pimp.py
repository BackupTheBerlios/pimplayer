#!/usr/bin/env python
import main
from pimp.extensions.tag import *
from pimp.extensions.context import *
from pimp.extensions.player_event import *
from pimp.core.song import *
from pimp.core.playlist import *
from pimp.core.db import File

import atexit,readline,os
historyPath = os.path.expanduser("~/.pimpstory")
def save_history(historyPath=historyPath):
    import readline
    readline.write_history_file(historyPath)

if os.path.exists(historyPath):
    readline.read_history_file(historyPath)

atexit.register(save_history)
del(atexit)
del(os)
del(readline)

from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed("")
ipshell() 


