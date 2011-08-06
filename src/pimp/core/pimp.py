"""This module contains the PlayerPlaylist class and some configuration variables."""
from player import *
from playlist import *
from song import *

from db import *
import common


class PlayerPlaylist(object,Player,Playlist):
	"""PlayerPlaylist is a Player and a Playlist of Song.
	Moreover, some actions on player (play,next ...) can be hooked
	(see commmon.Hook.HookMethod decorator)
	
	All methods of this class should be safe. For instance, the stop
	method test the status of the player to know if the stop action
	really occured.
	"""
	
	__metaclass__=common.Hook

	def __init__(self,playlist=[]):
		Player.__init__(self)
		Playlist.__init__(self,Song,playlist)

        @common.Hook.HookMethod
	def play(self,selector=Playlist.getCurrent):
		if Player.play(self,selector(self,setCurrent=True).path):
			return (Playlist.getCurrent(self).path
				,Playlist.getCurrent(self).duration)
		else : return None

        @common.Hook.HookMethod
	def next(self):	return self.play(Playlist.getNext)

        @common.Hook.HookMethod
	def prev(self):	return self.play(Playlist.getPrev)
            
	def playId(self,idx): 
            self.play(lambda a , setCurrent : Playlist.getById(a,idx,setCurrent))

	def playPos(self,idx): 
            self.play(lambda a , setCurrent : Playlist.getByPos(a,idx,setCurrent))

        @common.Hook.HookMethod
	def queue(self): return self.next()

        @common.Hook.HookMethod
        def stop(self):
            if Player.status(self) != 'stop':
		    pos=self.information()['position']
		    path=Playlist.getCurrent(self).path
		    Player.stop(self)
		    return (path,pos)
	    else: return None


        @common.Hook.HookMethod
        def pause(self):
            if Player.status(self) != 'stop':
                pos=self.information()['position']
                status=self.information()['status']
                if  status=="play":
                    status="pause"
                elif status=="pause":
                    status="unpause"
                Player.pause(self)
                return (Playlist.getCurrent(self).path,pos,status)
	    else : return None

        @common.Hook.HookMethod
	def seek(self,time):
		if Player.status(self) == 'stop':
			return None
                pos=self.information()['position']
		Player.seek(self,time)
		return (Playlist.getCurrent(self).path,pos,time)
		
	def information(self):
		return Info(Player.information(self).items() + Playlist.information(self).items())


player = PlayerPlaylist()
""" Main object """
