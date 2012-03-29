# import pimp.handlers.mpd
import mpdserver
import pimp.core.common
import threading

from pimp.core.pimp import player

import logging
logger=logging.getLogger("mpd_pimp")
logger.setLevel(logging.DEBUG)



def pimpToMpdPlaylist(playlist):
    return [{'file':e.getPath(),
             'title':'',
             'time':e.duration,
             'album':'',
             'artist':'',
             'track':0,
             'id':id(e)}
            for e in playlist]

def generateId(song):
    return id(song)

class MpdPlaylist(mpdserver.MpdPlaylist):
    def songIdToPosition(self,i):
        print "songid in songIdPos "+str(i) 
        for j in range(0,len(player)):
            if generateId(player[j])==i : 
                return j
            
    def handlePlaylist(self):
        return pimpToMpdPlaylist(player)

    def move(self,i,j):
        player.move(i,j)
    def version(self):
        return player.version()
    def delete(self,i):
        del(player[i])

class Status(mpdserver.Status):
    def items(self):
        args={'volume':player.volume()*100,
              'repeat':0,
              'random':0,
              'xfade':0}
        if player.status() == "play":
            return self.helper_status_play(elapsedTime=player.timePosition(),
                                           durationTime=player.timeDuration(),
                                           playlistSongNumber=player.getCurrentIdx(),
                                           playlistSongId=generateId(player[player.getCurrentIdx()]),
                                           **args)
        elif player.status() == "pause":
            return self.helper_status_pause(elapsedTime=player.timePosition(),
                                            durationTime=player.timeDuration(),
                                            playlistSongNumber=player.getCurrentIdx(),
                                            playlistSongId=generateId(player[player.getCurrentIdx()]),
                                            **args)
        elif player.status() == "stop":
            return self.helper_status_stop(**args)

class SetVol(mpdserver.SetVol):
    def handle_args(self,volume):
        return player.volume(float(volume)/100)

class PlayId(mpdserver.PlayId):
    def handle_args(self,songId):
        return player.play(self.playlist.songIdToPosition(songId))
class Play(mpdserver.Command):
    def handle_args(self):
        return player.play()

class Stop(mpdserver.Command):
    def handle_args(self):
        return player.stop()

class Next(mpdserver.Command):
    def handle_args(self):
        return player.next()
class Prev(mpdserver.Command):
    def handle_args(self):
        return player.prev()


class Add(mpdserver.Add):
    def handle_args(self,song):
        try:
            return player.appendByPath(song)
        except pimp.core.common.FileNotSupported as e:
            raise mpdserver.MpdCommandError(str(e)+" is not a supported file","add")

class CurrentSong(mpdserver.CurrentSong):
    def song(self):
        try:
            return self.helper_mkSong(file=player.current().getPath(),
                                      time=player.current().duration,
                                      title=player.current().getPath())
        except pimp.core.common.NoFileLoaded :
            return ""


class Clear(mpdserver.Command):
    def handle_args(self): del(player[:])


class Seek(mpdserver.Seek):
    def handle_args(self,songPosition,toSec):
        player.seek(toSec)
class Pause(mpdserver.Pause):
    def handle_pause(self): player.pause()
    def handle_unpause(self): player.pause()
    
class PimpMpdRequestHandler(mpdserver.MpdRequestHandler):pass
PimpMpdRequestHandler.commands['playid']=PlayId
PimpMpdRequestHandler.commands['add']=Add
PimpMpdRequestHandler.commands['clear']=Clear
PimpMpdRequestHandler.commands['status']=Status
PimpMpdRequestHandler.commands['setvol']=SetVol
PimpMpdRequestHandler.commands['stop']=Stop
PimpMpdRequestHandler.commands['seek']=Seek
PimpMpdRequestHandler.commands['pause']=Pause
PimpMpdRequestHandler.commands['currentsong']=CurrentSong
PimpMpdRequestHandler.commands['play']=Play
PimpMpdRequestHandler.commands['next']=Next
PimpMpdRequestHandler.commands['prev']=Prev
PimpMpdRequestHandler.Playlist=MpdPlaylist

def mpd(port):
    return mpdserver.Mpd(port,PimpMpdRequestHandler)
