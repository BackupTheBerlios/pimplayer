"""This module contains the PlayerPlaylist class and some configuration variables."""
from player import *
from playlist import *
from song import *

from db import *
import common


class PlayerPlaylist(Player,Playlist):
	"""PlayerPlaylist is a Player and a Playlist of Song.
	Moreover, all action on player (play,next ...) are logged.
	
	All methods of this class should be safe. For instance, the stop
	method test the status of the player to know if the stop action
	really occured.
	
	Decorator common.Guard.locked is used to ensure that only one event
	is emitted on a player action. For instance, the next method call
	the play method, and we don't want to emit two events. Be careful with thread !"""
	def __init__(self,playlist=[]):
		Player.__init__(self)
		Playlist.__init__(self,Song,playlist)

        @common.Guard.locked
	def play(self,selector=Playlist.getCurrent):
		if Player.play(self,selector(self,setCurrent=True).path):
			pitem=Playlist.getCurrent(self)
			Guard.guard(lambda : Play.Add(pitem.path,pitem.duration,"playid"))

        @common.Guard.locked
	def next(self):	
		self.play(Playlist.getNext)
		pitem=Playlist.getCurrent(self)
		Guard.guard(lambda : Play.Add(pitem.path,pitem.duration,"next"))

        @common.Guard.locked
	def prev(self):	
            self.play(Playlist.getPrev)
	    pitem=Playlist.getCurrent(self)
            Guard.guard(lambda : Play.Add(pitem.path,pitem.duration,"prev"))
            
	def playId(self,idx): 
            self.play(lambda a , setCurrent : Playlist.getById(a,idx,setCurrent))

	def playPos(self,idx): 
            self.play(lambda a , setCurrent : Playlist.getByPos(a,idx,setCurrent))


        @common.Guard.locked
	def queue(self): 
            self.next()
	    pitem=Playlist.getCurrent(self)
            Guard.guard(lambda : Play.Add(pitem.path,pitem.duration,"queue"))

        @common.Guard.locked
        def stop(self):
            if Player.status(self) != 'stop':
                pos=self.information()['position']
                Player.stop(self)
                Guard.guard(lambda : Stop.Add(Playlist.getCurrent(self).path,pos))

        @common.Guard.locked
        def pause(self):
            if Player.status(self) != 'stop':
                pos=self.information()['position']
                status=self.information()['status']
                if  status=="play":
                    status="pause"
                elif status=="pause":
                    status="unpause"
                Player.pause(self)
                Guard.guard(lambda : Pause.Add(Playlist.getCurrent(self).path,pos,status))


        @common.Guard.locked
	def seek(self,time):
                pos=self.information()['position']
		Player.seek(self,time)
                Guard.guard(lambda : Seek.Add(Playlist.getCurrent(self).path,pos,time))
		
	def information(self):
		return Info(Player.information(self).items() + Playlist.information(self).items())


# General configuaration and action on pimp
class Pimp:

	#
	def __init__(self):
		self._stdout=logging.StreamHandler()
		self._stdoutLogEnable=False
		
	# To see or not log messages in the console
	def toggleStdoutLog(self,level=logging.INFO):
		if self._stdoutLogEnable :
			logging.getLogger().removeHandler(self._stdout)
		else:
			logging.getLogger().addHandler(self._stdout)
		
		self._stdoutLogEnable=not self._stdoutLogEnable
		
		

defaultPlaylist = [
    "/home/mpd/zic/enc/no_doubt/tragic_kingdom/02-excuse_me_mr.flac",
    "/home/mpd/zic/enc/no_doubt/tragic_kingdom/03-just_a_girl.flac",
    "/home/mpd/zic/enc/no_doubt/tragic_kingdom/14-tragic_kingdom.flac",
    "/home/mpd/zic/enc/no_doubt/tragic_kingdom/05-different_people.flac"
    ]

player = PlayerPlaylist()
""" Main object """


#defaultPlayer = PlayerPlaylist(defaultPlaylist)

#else:
#	list.__repr__=list__repr__

def list__repr__(l):
	acc=""
	for e in l:
		acc=acc + str(e) + "\n"
	return acc

# else:
#     mpd_thread=mpd.startMpdHandler(player,mpd_port)
# #    mpdHandler=mpd.MpdHandler(mpd.MpdRequestHandler,defaultPlayer)

# if __name__ == "__main__":
#     mpd.startMpdHandler(player,mpd_port)

# else:
#     mpd_thread=mpd.startMpdHandler(player,mpd_port)
# #    mpdHandler=mpd.MpdHandler(mpd.MpdRequestHandler,defaultPlayer)


