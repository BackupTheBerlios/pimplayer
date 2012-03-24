""" This is a partial mpd handler. It permits to use mpd client to control
Pimp. Currently, a subset of playback commands are supported.

To launch a mpd server, use :class:`Mpd`.
Supported mpd commands are defined in :class:`MpdHandler`.


Note: 'command' and 'notcommand' commands seems to not be used by
gmpc. Then, we have to implement a lot of commands with dummy
respond. However, gmpc use 'command' command to allow user to play,
pause ...
"""
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
import time
import re 
import threading
import sys
#from pimp.core.playlist import * 
#from pimp.core.player import * 
#import pimp.core.db
import logging

logger=logging
logger.basicConfig(level=logging.DEBUG)

#logger.setLevel(logging.DEBUG)

class MpdServer(SocketServer.ThreadingMixIn,SocketServer.TCPServer):
    """Treat a request from a mpd client.
    Just a subset of mpd commands are supported. See Commands variable"""
    def __init__(self,RequestHandlerClass,port=6600):
        HOST, PORT = "localhost", port
        SocketServer.TCPServer.__init__(self,(HOST, PORT),RequestHandlerClass)


##################################
### Mpd supported return types ###
##################################
class MpdErrorMsgFormat(Exception):pass
class MpdCommandError(Exception):
    def __init__(self,msg="Unknown error",command="command is not specified"):
        self.command=command
        self.msg=msg
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} %s\n" % (self.command,self.msg)
class CommandNotSupported(MpdCommandError):
    def __init__(self,commandName):
        self.commandName=commandName
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} Command '%s' not supported\n" % (self.commandName,self.commandName)


class MpdReturnType(object):
    def checkType(self,cls):
        if type(self) is cls:
            return self.toMpdMsg()
        else: raise MpdErrorMsgFormat
    def toMpdMsg(self):
        logger.info("Dummy respond sent for command %s"%type(self))
        return ""

class PlChanges(MpdReturnType):pass


class Status(MpdReturnType):
    def __init__(self,volume=0,repeat=0,random=0,playlistVersion=0,playlistLength=1,xfade=0):
        "Status is set to 'stop' by default. Use :method:play or :method:pause to set status"
        self.volume=volume
        self.repeat=repeat
        self.random=random
        self.playlistVersion=playlistVersion
        self.playlistLength=playlistLength
        self.xfade=xfade
        self.state="stop"
    
    def play(self,elapsedTime,durationTime,playlistSongNumber=-1,playlistSongId=-1):
        self.state="play"
        self.elapsedTime=elapsedTime
        self.durationTime=durationTime
        self.playlistSongNumber=playlistSongNumber
        self.playlistSongId=playlistSongId
        return self

    def pause(self,elapsedTime,durationTime,playlistSongNumber=-1,playlistSongId=-1):
        self.state="pause"
        self.elapsedTime=elapsedTime
        self.durationTime=durationTime
        self.playlistSongNumber=playlistSongNumber
        self.playlistSongId=playlistSongId

        return self


    def toMpdMsg(self):
        if self.state=="pause" or self.state=="play":
            optionnal=(("song: %d\n" % self.playlistSongNumber) + #(current song stopped on or playing, playlist song number)
                       ("songid: %d\n"% self.playlistSongId) + #(current song stopped on or playing, playlist songid)
                       ("time: %d:%d\n" % (self.elapsedTime,self.durationTime)))  #<int elapsed>:<time total> (of current playing/paused song)
        else: optionnal=""
        return (("volume: %d\n"%self.volume) + #(0-100)
                ("repeat: %d\n"%self.repeat) + #(0 or 1)
                ("random: %d\n"%self.random) + #(0 or 1) 
                ("playlist: %d\n"%self.playlistVersion) + #(31-bit unsigned integer, the playlist version number)
                ("playlistlength: %d\n"%self.playlistLength)+ #(integer, the length of the playlist)
                ("xfade: %d\n"%self.xfade) + #(crossfade in seconds) 
                ('state: %s\n'%self.state) + #("play", "stop", or "pause")
                optionnal
                ) 
#                ('bitrate') + #<int bitrate> (instantaneous bitrate in kbps)
#                ('audio') + #<int sampleRate>:<int bits>:<int channels>
#                ('updating_db') + #<int job id>
#                ('error') + #if there is an error, returns message here
#                ('nextsong: 0\n') + #(next song, playlist song number >=mpd 0.15)
#                ('nextsongid: 0\n') + #(next song, playlist songid>=mpd 0.15)

class MpdPlaylist(MpdReturnType):
    def __init__(self,mpdSongs):
        self.playlist=mpdSongs
        
    def toMpdMsg(self):
        acc=""
        for i in self.playlist:
            acc+=i.toMpdMsg()
        return acc

class MpdSong(MpdReturnType):
    """ Generate songs information for mpd clients """
    def __init__(self,file,title="",time=0,album="",artist="",track=0,playlistPosition=0,id=0):
        self.file=file
        self.title=title
        self.time=time
        self.album=album
        self.artist=artist
        self.track=track
        self.playlistPosition=playlistPosition
        self.id=id

    def toMpdMsg(self):
        return (("file: %s\n"%self.file)+
                ("Time: %d\n"%self.time)+
                ("Album: %s\n"%self.album)+
                ("Artist: %s\n"%self.artist)+
                ("Title: %s\n"%self.title)+
                ("Track: %d\n"%self.track)+
                ("Pos: %d\n"%self.playlistPosition)+
                ("Id: %d\n"%self.id))

class Outputs(MpdReturnType):
    def toMpdMsg(self):
        return (("outputid: 0\n") + # <int output> the output number
                ("outputname: test\n") + # <str name> the name as defined in the MPD configuration file
                ("outputenabled: 1\n")) # <int enabled> 1 if enabled, 0 if disabled 

class ListPlaylistInfo(MpdReturnType):pass # Since 0.12
class LsInfo(MpdReturnType):pass # Since 0.12
class TagTypes(MpdReturnType):pass # Since 0.12

class Stats(MpdReturnType):
    def toMpdMsg(self):
        return (("artists: -1\n") +  #number of artists
                ("albums: -1\n") +  #number of albums
                ("songs: -1\n") +  #number of songs
                ("uptime: -1\n") +  #daemon uptime (time since last startup) in seconds
                ("playtime: -1\n") +  #time length of music played
                ("db_playtime: -1\n") +  #sum of all song times in db
                ("db_update: -1\n"))  #last db update in UNIX time 

class Commands(MpdReturnType): # Not used by gmpc
    def toMpdMsg(self):
        return (("command: status\n")  #number of artists
                + ("command: outputs\n")
                + ("command: pause\n") 
                + ("command: stop\n")
                + ("command: play\n")
                )
class NotCommands(MpdReturnType): # Not used by gmpc
    def toMpdMsg(self):
        return (("command: tagtypes\n") +  #number of artists
                ("command: lsinfo\n"))

class MpdRequestHandler(SocketServer.StreamRequestHandler):
    """ Manage the connection with a mpd client """
    def __init__(self, request, client_address, server):
        logger.debug( "Client connected (%s)" % threading.currentThread().getName())
        SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)

    def handle(self):
        """ Handle connection with mpd client. It gets client command,
        execute it and send a respond."""
        welcome="OK MPD 0.16.0\n"
        self.request.send(welcome)
        while True:
            msg=""
            try:
                cmdlist=None
                cmds=[]
                while True:
                    self.data = self.rfile.readline().strip()
                    if len(self.data)==0 : raise IOError #To detect last EOF
                    if self.data == "command_list_ok_begin":
                        cmdlist="list_ok"
                    elif self.data == "command_list_begin":
                        cmdlist="list"
                    elif self.data == "command_list_end":
                        break
                    else:
                        cmds.append(self.data)
                        if not cmdlist:break
                logger.debug("Commands received from %s" % self.client_address[0])
                try:
                    for c in cmds:
                        logger.debug("Command '" + c + "'...")
                        msg=msg+self.cmdExec(c)
                        if cmdlist=="list_ok" :  msg=msg+"list_OK\n"
                except MpdCommandError as e:
                    msg=e.toMpdMsg()
                except : raise
                else:
                    msg=msg+"OK\n"
                logger.debug("Message sent:\n\t\t"+msg.replace("\n","\n\t\t"))
                self.request.send(msg)
            except IOError,e:
                logger.debug("Client disconnected (%s)"% threading.currentThread().getName())
                break

    def cmdExec(self,c):
        """ Execute mpd client command. Take a string, parse it and
        execute the corresponding server.Command function."""
        try:
            pcmd=[m.group() for m in re.compile('(\w+)|("([^"])+")').finditer(c)] # WARNING An argument cannot contains a '"'
            cmd=pcmd[0]
            args=[a[1:len(a)-1] for a in pcmd[1:]]
            logger.debug("Command executed : %s %s" % (cmd,args))
#            msg=self.Command[cmd](self,args)
            msg=self.cmdParse(cmd,args)
            if msg==None : msg=""
        except KeyError:
            logger.warning("Command '%s' is not supported!" % cmd)
            msg=""
        # except IndexError:
        #     logger.debug("Playlist may be empty when command %s occured" % cmd)
        #     msg=""
        except MpdCommandError : raise
        except :
            logger.critical("Unexpected error on command %s: %s" % (c,sys.exc_info()[0]))
            raise
        logger.debug("Respond:\n\t\t"+msg.replace("\n","\n\t\t"))
        return msg

    def cmdParse(self,cmd,args):
        if cmd=="status": return self.status().checkType(Status)
        elif cmd=="notcommands": return self.notcommands().checkType(NotCommands)
        elif cmd=="outputs": return self.outputs().checkType(Outputs)
        elif cmd=="listplaylistinfo" : return self.listplaylistinfo(args[0]).checkType(ListPlaylistInfo)
        elif cmd=="stats" : return self.stats().checkType(Stats)
        elif cmd=="commands" : return self.commands().checkType(Commands)
        elif cmd=="notcommands" : return self.notcommands().checkType(NotCommands)
        elif cmd=="lsinfo" : return self.lsinfo(args).checkType(LsInfo)
        elif cmd=="tagtypes" : return self.tagtypes().checkType(TagTypes)
        elif cmd=="currentsong" : return self.currentsong().checkType(MpdSong)
        elif cmd=="plchanges" : return self.plchanges(int(args[0])).checkType(PlChanges)
        elif cmd=="playlistid" : return self.playlistid(int(args[0])).checkType(MpdSong)
        elif cmd=="playlistinfo": return self.playlistinfo([int(a) for a in args]).checkType(MpdPlaylist)
#         elif cmd=="playlistinfo" : return self.playlist_info(args) 
#         elif cmd=="plchanges" : return self.plchanges 
#         elif cmd=="lsinfo" : return self.lsinfo(args) 
#         elif cmd=="add" : return self.add(args) 
#         elif cmd=="play" : return self.play(args) 
#         elif cmd=="stop":return self.stop(args) 
#         elif cmd=="currentsong":return self.currentsong(args) 
#         elif cmd=="next" : return self.next(args) 
#         elif cmd=="previous" : return self.prev(args) 
# #        elif cmd=="listplaylists" : (lambda a (args)  b :"")(args) 
#         elif cmd=="playid" : return self.playid(args) 
#         elif cmd=="pause" : return self.pause(args) 
#         elif cmd=="delete" : return self.delete(args) 
#         elif cmd=="deleteid" : return self.deleteid(args) 
#         elif cmd=="clear" : return self.clear(args) 
#             #"seekid":seek(args) 
#         elif cmd=="seek":return self.seek(args) 
#         elif cmd=="move":return self.move(args) 
#         elif cmd=="moveid":return self.moveid(args) 
#         elif cmd=="count":return self.count(args) 
        else:
            logger.warning("Command '%s' is not supported!" % cmd)
            raise CommandNotSupported(cmd)




    ##############################
    ### Mpd supported commands ###
    ##############################

    def commands(self):return Commands()
    def notcommands(self):return NotCommands()
    def outputs(self):return Outputs()
    def status (self):return Status(98).play(10,100)
    def notcommands(self):return NotCommands()
    def lsinfo(self,paths):
        return LsInfo()
    def listplaylistinfo(self,playlistName):return ListPlaylistInfo()
    def stats(self):return Stats()
    def tagtypes(self):return TagTypes()
    def currentsong(self):return MpdSong("undefined")
    def plchanges(self,version):
        print version
        return PlChanges()
    def playlistid(self,songId):
        """To get song information by playlist id"""
        return MpdSong("undefined")
    def playlistinfo(self,songPositions):return MpdPlaylist([MpdSong("undefined")])



    # def plchanges(self,args):return ""
    # def playlist_info(self,args):return ""
    # def add(self,args): return ""
    # def play(self,args): return ""
    # def stop(self,args):return ""
    # def currentsong(self,args):return ""
    # def next(self,args):return ""
    # def prev(self,args):return ""
    # def playid(self,args):return ""
    # def pause(self,args):return ""
    # def delete(self,args):return ""
    # def deleteid(self,args):return ""
    # def clear(self,args):return ""
    # def volume(self,value):return ""
    # def seek(self,args):return ""
    # def move(self,args):return ""
    # def moveid(self,args):return ""
    # def count(self,args):
    #     """Commamnd example: count "album" "Aucune ..tiquette"
    #     """
    #     return ("songs: 0\n" +
    #             "playtime: 0\n")






class Mpd(object):
    """ Create the mpd handle server, binding to localhost on port 'port'.
    If port is not specified, the default MpdHandler port is used (6600)."""
    def __init__(self,port=None,mpdRequestHandler=MpdRequestHandler):
        logger.info("Mpd Server is listening on port " + str(port))
        if port:
            Mpd.server=MpdServer(mpdRequestHandler,port)
        else:
            Mpd.server=MpdServer(mpdRequestHandler)
            
        Mpd.thread = threading.Thread(target=Mpd.server.serve_forever)
        Mpd.thread.setDaemon(True)
        Mpd.thread.start()
        logger.debug(("mpd",Mpd.thread))
        
    def quit(self):
        """ Stop mpd server """
        Mpd.server.shutdown()
