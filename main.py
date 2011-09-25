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
usage = "usage: %prog -p MPD_PORT -d DATABASE -u DB_USERNAME --db-passwd=PASSWRD [options]"
parser = OptionParser(usage)
parser.add_option("-p", "--mpd-port", dest="mpd_port", type=int,
                  help="mpd handler port")
parser.add_option("-d", "--db-database", dest="db_database",
                  help="database used by pimp")
parser.add_option("-u", "--db-username", dest="db_username",
                  help="username of database")
parser.add_option("--db-passwd", dest="db_password",
                  help="password to access database")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose",
                  help="print message on stdout (message are also written in .pimp.log)")

(options, args) = parser.parse_args()
if (options.mpd_port == None 
    or options.db_database == None 
    or options.db_username == None 
    or options.db_password == None) :
    parser.error(usage)
    exit()
    
import sys,os
sys.path.insert(0,os.path.abspath("./src/"))

# For verbose mode
# ================
from pimp.core.common import Log
if options.verbose: Log.toggle_stdout()

# Start Pimp player
# =================
from pimp.core.pimp import player
import pimp.extensions.context
try:
    pimp.extensions.context.loadContext(player,"default")
except Exception as e: print e
else:
    print "Loading default context ..."


# Initialisation of extensions
# ============================
import pimp.extensions.player_event
import pimp.extensions.tag

# Initialisation of handlers
# ==========================
mpd_port = options.mpd_port
""" Port used by the mpd request handler """
from pimp.handlers.mpd import Mpd
mpd=Mpd(player,mpd_port)

# Initialisation of database
# ==========================
database=options.db_database
""" Name of database """
user = options.db_username
""" User to use the database """
pwd =  options.db_password
""" Password of database user"""
from pimp.core.db import Db
Db.Configure(user,pwd,database)


print "Welcome on Pimp"
print "---------------"
print "Pimp is listenin mpd client on port %d " % mpd_port
print "Pimp is using %s database with user %s " % (database,user)
print ""

import pimp.extensions.context

def quit():
	""" To leave Pimp """
        print "Saving context ..."
        pimp.extensions.context.saveContext(player,"default")
	print "Quitting mpd ..."
	mpd.quit()
	print "Quitting player ..."
	player.quit()
	print "Quitting Pimp. Bye" 
	exit()

import atexit
atexit.register(quit)
del(atexit)


if __name__ == "__main__":
	while mpd.thread.isAlive():
		try:
                    mpd.thread.join(2)
		except KeyboardInterrupt:break;

