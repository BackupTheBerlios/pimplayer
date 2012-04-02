""" A context is a playlist with current song and a player state. 
It's then possible to store and restore the pimp state.
"""

import pickle
import pimp.core.playlist
import os.path
import atexit
import os

context_dir=os.path.expanduser("~/.pimp/contexts/")
""" Directory where context files are written """

class ContextNotExist(Exception):pass

def saveContext(player,name):
	""" Write a context of name 'name'. Currently, the the playlist state is supported """
        c = context_dir+name
        f = open(c, 'w')
        pl=pimp.core.playlist.Playlist.__getstate__(player)
        pickle.dump(pl,f)
        f.close()

def loadContext(player,name):
	""" Load a context of name 'name'. Currently, the the playlist state is supported """
	try :
		c = context_dir+name
		f = open(c, 'r')
		d = pickle.load(f)
		pimp.core.playlist.Playlist.__setstate__(player,d)
		f.close
	except IOError : raise ContextNotExist("Context %s doesn't exist" % c)

def listContext():
	root,dirs,files=os.walk(context_dir).next()
	return files
def getPlaylistFromContext(name):
	""" Get a playlist object from a context"""
	try :
		c = context_dir+name
		f = open(c, 'r')
		d = pickle.load(f)
		f.close
		return d['playlist']
	except IOError : raise ContextNotExist("Context %s doesn't exist" % c)


def deleteContext(name):
	playlistName=context_dir+name
	if os.path.exists(playlistName):
		os.remove(playlistName)


#def enable(player,name):
#	loadContext(player,name)
#	atexit.register(lambda : saveContext(player,name))

