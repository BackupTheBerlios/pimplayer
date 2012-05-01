# import pimp.handlers.mpd
import mpdserver
import pimp.core.common
import threading

from pimp.core.pimp import player
import pimp.extensions.context

import logging
logger=logging.getLogger("mpd_pimp")
logger.setLevel(logging.DEBUG)


def pimpSongToMpdPlaylistSongs(playlist):
    return [mpdserver.MpdPlaylistSong(file=e.getPath(),
                                      songId=generateId(e),
                                      title='',
                                      time=e.duration,
                                      album='',
                                      artist='',
                                      track=0)
            for e in playlist]

def generateId(song):
    id64 = id(song)
    return id64 & (pow(2,32)-1)

class MpdPlaylist(mpdserver.MpdPlaylist):
    def songIdToPosition(self,i):
        for j in range(0,len(player)):
            if generateId(player[j])==i : 
                return j
            
    def handlePlaylist(self):
        return pimpSongToMpdPlaylistSongs(player)

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
        status=player.status()
        if status == "play":
            return self.helper_status_play(elapsedTime=player.timePosition(),
                                           durationTime=player.timeDuration(),
                                           playlistSongNumber=player.getCurrentIdx(),
                                           playlistSongId=generateId(player[player.getCurrentIdx()]),
                                           **args)
        elif status == "pause":
            return self.helper_status_pause(elapsedTime=player.timePosition(),
                                            durationTime=player.timeDuration(),
                                            playlistSongNumber=player.getCurrentIdx(),
                                            playlistSongId=generateId(player[player.getCurrentIdx()]),
                                            **args)
        elif status == "stop":
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
    def songs(self):
        try:
            return [mpdserver.MpdPlaylistSong(file=player.current().getPath(),
                                              songId=generateId(player.current()),
                                              time=player.current().duration,
                                              title=player.current().getPath(),
                                              playlistPosition=player.currentIdx())]
        except pimp.core.common.NoFileLoaded :
            return ""


class Clear(mpdserver.Command):
    def handle_args(self): 
        player.stop()
        del(player[:])


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
class ListPlaylistInfo(mpdserver.ListPlaylistInfo): # Since 0.12
    def songs(self):
        try:
            p=pimp.extensions.context.getPlaylistFromContext(self.args['playlistName'])
        except pimp.extensions.context.ContextNotExist:p=[]
        return [mpdserver.MpdPlaylistSong(file=s.getPath(),
                                          time=s.duration,
                                          title=s.getPath(),
                                          songId=generateId(s)) for s in p]
    
import os
class LsInfo(mpdserver.LsInfo):
    """ Doesn't work with mpc when a filepath begins with a '/'."""
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
                ("Album",""),
                ("Track",""),
                ("Genre","")]
    def items(self):
        if self.args['directory'] == "/":
            root=self.rootDir+self.args['directory']
        else:
            root=self.args['directory']+"/"
        try:
            root,dirs,files=os.walk(root).next()
        except StopIteration:
            return []
        ret= ([("directory",(root+i)) for i in dirs if not i.startswith(".")] +
              sum([self.__helperFile((root+i)) for i in files if not i.startswith(".")],[]))
        return ret
    
class PimpMpdRequestHandler(mpdserver.MpdRequestHandler):pass
def mpd(port):
    mpd=mpdserver.MpdServerDaemon(port,PimpMpdRequestHandler)
    mpd.requestHandler.RegisterCommand(mpdserver.Outputs)
    mpd.requestHandler.RegisterCommand(PlayId)
    mpd.requestHandler.RegisterCommand(Add)
    mpd.requestHandler.RegisterCommand(Add)
    mpd.requestHandler.RegisterCommand(Clear)
    mpd.requestHandler.RegisterCommand(Status)
    mpd.requestHandler.RegisterCommand(SetVol)
    mpd.requestHandler.RegisterCommand(Stop)
    mpd.requestHandler.RegisterCommand(Seek)
    mpd.requestHandler.RegisterCommand(Pause)
    mpd.requestHandler.RegisterCommand(CurrentSong)
    mpd.requestHandler.RegisterCommand(Play)
    mpd.requestHandler.RegisterCommand(Next)
    mpd.requestHandler.RegisterCommand(Prev)
    mpd.requestHandler.RegisterCommand(LsInfo)
    mpd.requestHandler.RegisterCommand(Random)
# Playlist Management
    mpd.requestHandler.RegisterCommand(ListPlaylists)
    mpd.requestHandler.RegisterCommand(Load)
    mpd.requestHandler.RegisterCommand(Save)
    mpd.requestHandler.RegisterCommand(Rm)
    mpd.requestHandler.RegisterCommand(ListPlaylistInfo)
    PimpMpdRequestHandler.Playlist=MpdPlaylist
    logger.info("Supported Mpd Commands command name | allowed users: ")
    for e in mpd.requestHandler.SupportedCommand():
        logger.info("\t%s"%str(e))
