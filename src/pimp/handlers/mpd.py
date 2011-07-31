""" A partial mpd handler. It permits to use mpd client to control
Pimp. Currently, a subset of playback commands are supported."""

import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
import time
import re 
import threading

#import test
from pimp.core.playlist import * 
from pimp.core.player import * 


# This class treats a request from a mpd client.
# Just a subset of mpd commands are supported. See Commands variable
class MpdHandler(SocketServer.ThreadingMixIn,SocketServer.TCPServer):
    Verbose=1

    def __init__(self,RequestHandlerClass,playerPlaylist,port=6600):
        self.player=playerPlaylist
        HOST, PORT = "localhost", port
        SocketServer.TCPServer.__init__(self,(HOST, PORT),RequestHandlerClass)
        

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
                
    def toMpdPlaylist(self,playlist):
        ret=""
        pos=0
        if playlist == [] : return ""
        for i in playlist:
            ret=ret+self.toMpdPlaylistItem(i.path,i.id,pos,i.duration)
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
    
    

    def toMpdDir(self,path):
        return "directory: "+path+"\n"

    def plchanges(self,args):return self.toMpdPlaylist(self.player._playlist)

    def playlist_info(self,args):return self.toMpdPlaylist(self.player._playlist)

    def add(self,args): self.player.append(args[0])

    def play(self,args):
        if args:
            self.player.playPos(int(args[0]))
            return
            
        if self.player.status() == "pause":
            self.player.pause()
        else:
            self.player.play()
    def stop(self,args):self.player.stop()
    def currentsong(self,args):
        if self.player.getCurrent() == None:
            return None
        else:
            return self.toMpdPlaylistItem(self.player.getCurrent().path,self.player.getCurrent().id,self.player.getCurrentPos(),self.player.getCurrent().duration)
    def next(self,args):self.player.next()
    def prev(self,args):self.player.prev()
    def playid(self,args):self.player.playId(int(args[0]))
    def pause(self,args):self.player.pause()
    def delete(self,args):self.player.remove(int(args[0]))
    def deleteid(self,args):self.player.removeId(int(args[0]))
    def clear(self,args):self.player.clear()
    def volume(self,args):self.player.volume(float(args[0])/100)
    def seek(self,args):
        print args
        self.player.seek(int(args[1]))
    def move(self,args):self.player.move(int(args[0]),int(args[1]))
    def moveid(self,args):self.player.moveById(int(args[0]),int(args[1]))
    

   #Doesn't work
    def ls_info(self,args):
        path=args[0].replace('"','')
        toMpd={'file':self.toMpdPlaylistItem ,
                'dir':self.toMpdDir}
        return ''.join([toMpd[t](f) for (f,t) in Library().lstype(path) if t!=None])

    Command={
        "status" : status,
        "playlistinfo" : playlist_info,
        "plchanges" : plchanges,
        #        "lsinfo" : ls_info,
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
        "seekid":seek,
        "seek":seek,
        "move":move,
        "moveid":moveid
        }

# This class manages the connection with a mpd client
class MpdRequestHandler(SocketServer.StreamRequestHandler):
    Verbose = 1

    def __init__(self, request, client_address, server):
        logging.info( "Client connected (%s)" % threading.currentThread().getName())
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
                logging.info("Commands received from %s: " % self.client_address[0])
                for c in cmds:
                    logging.info("Command '" + c + "'...")
                    msg=msg+self.cmdExec(c)
                    if cmdlist=="list_ok" :  msg=msg+"list_OK\n"
                msg=msg+"OK\n"
                logging.debug("Message sent:\n\t\t"+msg.replace("\n","\n\t\t"))
                self.request.send(msg)
            except IOError,e:
                logging.info("Client disconnected (%s)"% threading.currentThread().getName())
                break

    def cmdExec(self,c):
        try:
            pcmd=[m.group() for m in re.compile('(\w+)|("([^"])+")').finditer(c)] # WARNING An argument cannot contains a '"'
            cmd=pcmd[0]
            args=[a[1:len(a)-1] for a in pcmd[1:]]
            logging.info("Command received : %s %s" % (cmd,args))
            msg=self.server.Command[cmd](self.server,args)
            if msg==None : msg=""
        except KeyError:
            logging.info("Command '%s' is not supported!" % cmd)
            msg=""
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        logging.debug("Respond:\n\t\t"+msg.replace("\n","\n\t\t"))
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
        if port:
            Mpd.server=MpdHandler(MpdRequestHandler,player,port )
        else:
            Mpd.server=MpdHandler(MpdRequestHandler,player)
            
        Mpd.thread = threading.Thread(target=Mpd.server.serve_forever)
        Mpd.thread.setDaemon(True)
        Mpd.thread.start()

    def quit(self):
        Mpd.server.shutdown()
