""" A partial mpd handler. It permits to use mpd client to control
Pimp. Currently, a subset of playback commands are supported."""

import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
import time
import re 
import threading

from pimp.core.playlist import * 
from pimp.core.player import * 
import pimp.core.db


logger=logging.getLogger("mpd")
logger.setLevel(logging.DEBUG)

class MpdHandler(SocketServer.ThreadingMixIn,SocketServer.TCPServer):
    """This class treats a request from a mpd client.
    Just a subset of mpd commands are supported. See Commands variable"""
    def __init__(self,RequestHandlerClass,playerPlaylist,port=6600):
        self.player=playerPlaylist
        HOST, PORT = "localhost", port
        SocketServer.TCPServer.__init__(self,(HOST, PORT),RequestHandlerClass)

    def commands(self,args):
        acc=""
        for i in self.Command.keys():
            acc+="command: %s\n" % i
        return acc

    def outputs(self,args):
        return ("outputid: 0\n" +
                "outputname: mpd alsa device\n"+
                "outputenabled: 1\n")

    def status (self,args):
        infos=self.player.information()
        return ((infos['volume'] != None and "volume: %d\n" % (infos['volume']*100) or "") +
                ("repeat: 1\n") +
                ("random: 0\n") +
                ("single: 0\n") +
                ("consume: 0\n") +
                (infos['version'] != None and "playlist: %s\n" % (infos['version']) or "playlist: 0\n" ) +
                (infos['length'] != None and "playlistlength: %d\n" % (infos['length']) or "playlistlength: 0\n" )+
                ("xfade: 0\n") + 
                ("mixrampdb: 0.000000\n") + 
                ("mixrampdelay: nan\n") +
                (infos['status'] != None and "state: %s\n" % (infos['status']) or "" )+
                (infos['currentPos'] != None and "song: %d\n" % (infos['currentPos']) or "")+
                (infos['currentId'] != None and "songid: %d\n" % (infos['currentId']) or "")+
                ((infos['position'] != None and infos['duration'] != None) and "time: %d:%d\n" % (infos['position'],infos['duration']) or "")+
                (infos['position'] != None and "elapsed: %d.000 \n" % (infos['position']) or "")+
                ("bitrate: 1\n")+
                ("audio: 0:?:0\n")+
                ("nextsong: 1\n") +
                ("nextsongid: 1\n"))

    def __idToIdx(self,id):
        return ([e.id for e in self.player]).index(id)
                
    def toMpdPlaylist(self,playlist):
        ret=""
        pos=0
        if playlist == [] : return ""
        for i in playlist:
            ret=ret+self.toMpdPlaylistItem(i.getPath(),i.id,pos,i.duration)
            pos=pos+1
        return ret


    def toMpdPlaylistItem(self,path,idx,pos,duration):
        if path==None : return ""
        return ("file: %s\n" % path +
                "Last-Modified: 2011-01-16T17:49:15Z\n" +
                "Time: %s\n" % duration +
#                "Artist: No Doubt\n" +
#                "Title: Spiderwebs\n" +
#                "Album: Tragic Kingdom\n" +
#                "Date: 1995\n" +
#                "Genre: Other\n" +
#                "Track: 01\n" +
                "Pos: %d\n" % pos +
                "Id: %d\n"% idx)
    
    
    def __toMpdFile(self,path,duration):
        return ("file: %s\n" % path +
                "Last-Modified: 2011-01-16T17:49:15Z\n" +
                "Time: %s\n" % duration +
                "Artist: No Doubt\n" +
                "Title: Spiderwebs\n" +
                "Album: Tragic Kingdom\n")
    

    def lsinfo(self,args):
#        try :
            if args[0] == '/':
                return "directory: lasts 50\n"
            elif args[0] == 'lasts 50':
                files=pimp.core.db.File.Lasts(50)
                acc=""
                for f in files:
                    acc+=self.__toMpdFile(f.path,f.duration)
                return acc
            else:
                return ""
#        except KeyError as e:
#            print e
#            exit
                


    def plchanges(self,args):return self.toMpdPlaylist(self.player[:])

    def playlist_info(self,args):return self.toMpdPlaylist(self.player[:])

    def add(self,args): self.player.appendByPath(args[0])

    def play(self,args):
        if args:
            self.player.play(int(args[0]))
            return
            
        if self.player.status() == "pause":
            self.player.pause()
        else:
            self.player.play()
    def stop(self,args):self.player.stop()
    def currentsong(self,args):
        if not self.player.isEmpty() and self.player.current() != None:
            return self.toMpdPlaylistItem(self.player.current().getPath(),
                                          self.player.current().id,
                                          self.player.getCurrentIdx(),
                                          self.player.current().duration)
        else : return ""

    def next(self,args):self.player.next()
    def prev(self,args):self.player.prev()
    def playid(self,args):self.player.play(self.__idToIdx(int(args[0])))
    def pause(self,args):self.player.pause()
    def delete(self,args):del(self.player[int(args[0])])
    def deleteid(self,args):del(self.player[self.__idToIdx(int(args[0]))])
    def clear(self,args):del(self.player[:])
    def volume(self,args):self.player.volume(float(args[0])/100)
    def seek(self,args):
        print args
        self.player.seek(int(args[1]))
    def move(self,args):self.player.move(int(args[0]),int(args[1]))
    def moveid(self,args):
        ifrom = self.__idToIdx(int(args[0]))
        ito = self.__idToIdx(int(args[1]))
        self.player.move(ifrom,ito)
    


    Command={
        "outputs": outputs,
#        "commands" : commands,
        "status" : status,
        "playlistinfo" : playlist_info,
        "plchanges" : plchanges,
        "lsinfo" : lsinfo,
        "add" : add,
        "play" : play,
        "stop":stop,
        "currentsong":currentsong,
        "next" : next,
        "previous" : prev,
        "listplaylists" : (lambda a , b : ""),
        "playid" : playid,
        "pause" : pause,
        "delete" : delete,
        "deleteid" : deleteid,
        "clear" : clear,
        "setvol": volume,
        #"seekid":seek,
        "seek":seek,
        "move":move,
        "moveid":moveid
        }

class MpdRequestHandler(SocketServer.StreamRequestHandler):
    """ This class manages the connection with a mpd client """
    def __init__(self, request, client_address, server):
        logger.debug( "Client connected (%s)" % threading.currentThread().getName())
        SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)

    def handle(self):
        # self.request is the TCP socket connected to the client
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
                logger.debug("Commands received from %s: " % self.client_address[0])
                for c in cmds:
                    logger.debug("Command '" + c + "'...")
                    msg=msg+self.cmdExec(c)
                    if cmdlist=="list_ok" :  msg=msg+"list_OK\n"
                msg=msg+"OK\n"
                logger.debug("Message sent:\n\t\t"+msg.replace("\n","\n\t\t"))
                self.request.send(msg)
            except IOError,e:
                logger.debug("Client disconnected (%s)"% threading.currentThread().getName())
                break

    def cmdExec(self,c):
        try:
            pcmd=[m.group() for m in re.compile('(\w+)|("([^"])+")').finditer(c)] # WARNING An argument cannot contains a '"'
            cmd=pcmd[0]
            args=[a[1:len(a)-1] for a in pcmd[1:]]
            logger.debug("Command received : %s %s" % (cmd,args))
            msg=self.server.Command[cmd](self.server,args)
            if msg==None : msg=""
        except KeyError:
            logger.warning("Command '%s' is not supported!" % cmd)
            msg=""
        # except IndexError:
        #     logger.debug("Playlist may be empty when command %s occured" % cmd)
        #     msg=""
        except:
            logger.critical("Unexpected error on command %s: %s" % (c,sys.exc_info()[0]))
            raise
        logger.debug("Respond:\n\t\t"+msg.replace("\n","\n\t\t"))
        return msg
            

    def __parseCmd(self,cmd):
        part=cmd.partition(" ")
        action=part[0]
        args=part[2]
        return (action,args)



# Create the mpd handle server, binding to localhost on port 'port'.
# If port is not specified, the default MpdHandler port is used (6600).
class Mpd(object):
    def __init__(self,player,port=None):
        logger.info("Mpd handler is listening on port %d"%port)
        if port:
            Mpd.server=MpdHandler(MpdRequestHandler,player,port )
        else:
            Mpd.server=MpdHandler(MpdRequestHandler,player)
            
        Mpd.thread = threading.Thread(target=Mpd.server.serve_forever)
        Mpd.thread.setDaemon(True)
        Mpd.thread.start()

    def quit(self):
        Mpd.server.shutdown()
