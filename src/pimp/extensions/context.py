""" A context is a playlist with current song and a player state. 
It's then possible to store and restore the pimp state.
"""

import pickle
import pimp.core.playlist
import os.path

context_dir=os.path.expanduser("~/.pimp/contexts/")

def saveContext(player,name):
    f = open(context_dir+name, 'w')
    pl=pimp.core.playlist.Playlist.__getstate__(player)
    pickle.dump(pl,f)
    f.close()

def loadContext(player,name):
    f = open(context_dir+name, 'r')
    d = pickle.load(f)
    pimp.core.playlist.Playlist.__setstate__(player,d)
    f.close



