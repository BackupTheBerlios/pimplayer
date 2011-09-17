""" A context is a playlist with current song and a player state. 
It's then possible to store and restore the pimp state.
"""

import pickle
import pimp.core.playlist
import os.path

context_dir=os.path.expanduser("~/.pimp/contexts/")

def saveContext(player,name):
        c = context_dir+name
        f = open(c, 'w')
        pl=pimp.core.playlist.Playlist.__getstate__(player)
        pickle.dump(pl,f)
        f.close()

def loadContext(player,name):
    try :
        c = context_dir+name
        f = open(c, 'r')
        d = pickle.load(f)
        pimp.core.playlist.Playlist.__setstate__(player,d)
        f.close
    except IOError : raise Exception("Context %s doesn't exist" % c)



