# import pimp.handlers.mpd
import mpdserver
import pimp.core.common
import threading

from pimp.core.pimp import player
import pimp.extensions.context

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
             'id':generateId(e)}
            for e in playlist]

def generateId(song):
    id64 = id(song)
    return id64 & (pow(2,32)-1)

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
        if i==player.getCurrentIdx():
            player.stop()
        del(player[i])

class Status(mpdserver.Status):
    def items(self):
        args={'volume':player.volume()*100,
              'repeat':0,
              'random':int(player.random()),
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

class Random(mpdserver.Random):
    def handle_args(self,state):
        player.random(bool(state))

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
                                      title=player.current().getPath(),
                                      id=generateId(player.current()))
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


class ListPlaylists(mpdserver.ListPlaylists):
    def handle_playlists(self):
        return pimp.extensions.context.listContext()

class Load(mpdserver.Load):
    def handle_args(self,playlistName):
        pimp.extensions.context.loadContext(player,playlistName)
class Save(mpdserver.Load):
    def handle_args(self,playlistName):
        pimp.extensions.context.saveContext(player,playlistName)
class Rm(mpdserver.Rm):
    def handle_args(self,playlistName):
        pimp.extensions.context.deleteContext(playlistName)

import os
class LsInfo(mpdserver.LsInfo):
    rootDir="/media/usb1"
    def handle_args(self,directory=None):
        if not directory:
            self.args['directory']="/"
    def __helperFile(self,filename):
        return [("file",filename),
                ("Last-Modified","2011-12-17T22:47:58Z"),
                ("Time","0"),
                ("Artist", ""),
                ("Title",filename),
                ("Track","")]
    def items(self):
        if self.args['directory'] == "/":
            root=self.rootDir+self.args['directory']
        else:
            root=self.args['directory']+"/"
        root,dirs,files=os.walk(root).next()
        ret= ([("directory",(root+i)) for i in dirs] +
              sum([self.__helperFile((root+i)) for i in files],[]))
        return ret
    
class PimpMpdRequestHandler(mpdserver.MpdRequestHandler):pass
PimpMpdRequestHandler.commands['playid']=PlayId
PimpMpdRequestHandler.commands['add']=Add
PimpMpdRequestHandler.commands['addid']=Add
PimpMpdRequestHandler.commands['clear']=Clear
PimpMpdRequestHandler.commands['status']=Status
PimpMpdRequestHandler.commands['setvol']=SetVol
PimpMpdRequestHandler.commands['stop']=Stop
PimpMpdRequestHandler.commands['seek']=Seek
PimpMpdRequestHandler.commands['pause']=Pause
PimpMpdRequestHandler.commands['currentsong']=CurrentSong
PimpMpdRequestHandler.commands['play']=Play
PimpMpdRequestHandler.commands['next']=Next
PimpMpdRequestHandler.commands['previous']=Prev
PimpMpdRequestHandler.commands['lsinfo']=LsInfo
PimpMpdRequestHandler.commands['random']=Random
# Playlist Management
PimpMpdRequestHandler.commands['listplaylists']=ListPlaylists
PimpMpdRequestHandler.commands['load']=Load
PimpMpdRequestHandler.commands['save']=Save
PimpMpdRequestHandler.commands['rm']=Rm

PimpMpdRequestHandler.Playlist=MpdPlaylist

def mpd(port):
    return mpdserver.Mpd(port,PimpMpdRequestHandler)
