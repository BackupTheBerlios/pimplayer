#!/usr/bin/env python

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

"""Launch IPython in a deamon thread."""
from pimp.extensions.context import *
from pimp.core.song import *
from pimp.core.playlist import *

from pimp.core.db import File

logger=logging.getLogger("ipimp")
logger.setLevel(logging.DEBUG)


#Shity hack to import module name if alreay loaded ...
import sys
if 'pimp.extensions.player_event' in sys.modules.keys():
     from pimp.extensions.player_event import *
if 'pimp.extensions.tag' in sys.modules.keys():
     from pimp.extensions.tag import *
if 'pimp.core.file' in sys.modules.keys():
     from pimp.core.file import *
if 'pimp.core.pimp' in sys.modules.keys():
     from pimp.core.pimp import *


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

import pimp.core.player

import threading
from IPython.Shell import IPShellEmbed

class Ipimp (threading.Thread):
     def __init__(self):
          threading.Thread.__init__(self)
          self.ipshell = IPShellEmbed(["-noconfirm_exit"])

     def run(self):
          logger.info("Ipimp is launched")
          self.ipshell()
          logger.info("Quit Ipimp")
          print "IPython exited ... (type Ctrl-C to exit Pimp)"
