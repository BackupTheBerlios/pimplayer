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

from optparse import OptionParser

# Check Arguments
# ===============
usage = "%prog -p MPD_PORT -d DATABASE -u DB_USERNAME --db-passwd=PASSWRD [options]"
parser = OptionParser(usage)
parser.add_option("-p", "--mpd-port", dest="mpd_port", type=int,
                  help="mpd handler port")
parser.add_option("-d", "--db-database", dest="db_database",
                  help="database used by pimp")
parser.add_option("--disable-db", 
                  action="store_true",dest="disable_db",default=False,
                  help="Enable Database [default: %default]")

parser.add_option("-i","--interactive", 
                  action="store_true",dest="interactive",default=False,
                  help="Interactive session via ipython [default: %default]")

parser.add_option("-r","--remote", 
                  action="store_true",dest="remote",default=False,
                  help="Run remote object with Pyro. Use pimpc.py to contact it [default: %default]")
parser.add_option("--remote-port", dest="remote_port", type=int,default=9998,
                  help="remote object handler port")

parser.add_option("-c","--enable_context", 
                  action="store_true",dest="enable_context",default=False,
                  help="Enable context extension [default: %default]")


parser.add_option("-u", "--db-username", dest="db_username",
                  help="username of database")
parser.add_option("--db-passwd", dest="db_password",
                  help="password to access database")
parser.add_option("-v",
                  action="store_true", dest="verbose",
                  help="print INFO message on stdout (message are also written in .pimp.log)")
parser.add_option("--verbosity",
                  dest="verbosity",default=None,type=int,
                  help="print message on stdout between 10 (debug) and 50 (warning)")

(options, args) = parser.parse_args()
    


# For verbose mode
# ================
from pimp.core.common import Log
if options.verbose:
    Log.toggle_stdout()
if options.verbosity:
    Log.stdout_level(options.verbosity)


# Start Pimp player
# =================
from pimp.core.pimp import player

if options.enable_context:
    import pimp.extensions.context
    try:
        pimp.extensions.context.loadContext(player,"default")
    except Exception as e: print e
    else:
        print "Loading default context ..."

# Initialisation of database
# ==========================
if(not options.disable_db):
    if (options.db_database == None 
        or options.db_username == None 
        or options.db_password == None) :
        parser.error("you must give database name, user and password or use --disable-db option.")
        exit()
    database=options.db_database
    user = options.db_username
    pwd =  options.db_password
    from pimp.core.db import Db
    Db.Configure(user,pwd,database)

# Initialisation of extensions
# ============================
if(not options.disable_db):
    import pimp.extensions.player_event
    import pimp.extensions.tag

# Initialisation of handlers
# ==========================
if (options.mpd_port != None ):
    mpd_port = options.mpd_port
    from pimp.handlers.mpd import Mpd
    from pimp.handlers.mpd_pimp import MpdRequestHandlerPimp
    mpd=Mpd(mpd_port,MpdRequestHandlerPimp)
#    from pimp.handlers.mpd import Mpd
#    mpd=Mpd(player,mpd_port)

import pimp.extensions.context

def quit():
	""" To leave Pimp """
        if options.enable_context:
            print "Saving context ..."
            pimp.extensions.context.saveContext(player,"default")
        if (options.mpd_port != None ):
            print "Quitting mpd ..."
            mpd.quit()
	print "Quitting player ..."
	player.quit()
	print "Quitting Pimp. Bye" 

import atexit
atexit.register(quit)
del(atexit)


if options.interactive :
    import pimp.handlers.ipimp
    ipimp=pimp.handlers.ipimp.Ipimp()
    ipimp.start()

if options.remote :
    import pimp.handlers.remote
    ipimp=pimp.handlers.remote.Remote(player,options.remote_port)

import threading
import time
if __name__ == "__main__":
    while (threading.activeCount()>1):
        try:
            time.sleep(1)
        except KeyboardInterrupt:print "";break;
        
