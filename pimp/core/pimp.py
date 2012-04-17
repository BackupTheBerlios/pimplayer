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

"""This module contains the PlayerPlaylist class and some configuration variables."""
from player import *
from playlist import *
from song import *

import common

logger=common.logging.getLogger("pimp.pimp")


class PlayerPlaylist(Player,Playlist,object):
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
		

	def __getstate__(self):
		playlist_state=Playlist.__getstate__(self)
		return player_state

	def __setstate__(self,state):
		self.stop()
		Playlist.__setstate__(self,state)

	def __play(self,selector=Playlist.current):
		if Player.play(self,selector(self,setCurrent=True).getPath()):
			return (Playlist.current(self)
				,Playlist.current(self).duration)
		else : return None

        @common.Hook.HookMethod
	def next(self):	return self.__play(Playlist.getNext)

        @common.Hook.HookMethod
	def prev(self):	return self.__play(Playlist.getPrev)
            
        @common.Hook.HookMethod
	def play(self,idx=None,**kwargs):
		if idx!=None:
			return self.__play(lambda a , setCurrent : Playlist.get(a,idx,setCurrent))
		else:
			return self.__play()

        @common.Hook.HookMethod
	def queue(self): 
		return self.next()

        @common.Hook.HookMethod
        def stop(self):
            if Player.status(self) != 'stop':
		    pos=self.information()['position']
		    path=Playlist.current(self)
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
                return (Playlist.current(self),pos,status)
	    else : return None

        @common.Hook.HookMethod
	def seek(self,time):
		if Player.status(self) == 'stop':
			return None
                pos=self.information()['position']
		Player.seek(self,time)
		return (Playlist.current(self),pos,time)
		
	def information(self):
		return Info(Player.information(self).items() + Playlist.information(self).items())



player = PlayerPlaylist()
""" Main object """
