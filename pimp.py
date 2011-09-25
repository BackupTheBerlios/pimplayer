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


