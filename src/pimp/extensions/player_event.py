"""This module defines some FileEvent and attach them to player
method. For instance, when PlayerPlaylist.stop is called, Stop.Add
method is executed"""
from pimp.core.db import *
from pimp.core.pimp import PlayerPlaylist

class Stop(Db.Base,FileEvent):
    __tablename__ = 'evt_stop'

    curTime = Column(Integer)

    def __init__(self,path,curTime,**kwds): 
        FileEvent.__init__(self,path,**kwds)
        self.curTime = curTime

PlayerPlaylist.AddHandler(
    PlayerPlaylist.stop,
    lambda (path,curTime) : Stop.Add(path,curTime))


class Play(Db.Base,FileEvent):
    PLAYID=0
    NEXT=1
    PREV=2
    QUEUE=3
    __tablename__ = 'evt_play'

    curTime = Column(Integer)
    status = Column(Integer)

    def __init__(self,path,curTime,status,**kwds): 
        self.curTime = curTime
        status2db={'playid':Play.PLAYID,'next':Play.NEXT,'prev':Play.PREV,'queue':Play.QUEUE}
        try:self.status = status2db[status]
        except KeyError:
            common.logging.error("Wrong status %s among %s" % (status,status2db.keys()))
            raise
            
        FileEvent.__init__(self,path,**kwds)

PlayerPlaylist.AddHandler(
    PlayerPlaylist.play,
    lambda (path,curTime) : Play.Add(path,curTime,"playid"))
PlayerPlaylist.AddHandler(
    PlayerPlaylist.next,
    lambda (path,curTime) : Play.Add(path,curTime,"next"))
PlayerPlaylist.AddHandler(
    PlayerPlaylist.prev,
    lambda (path,curTime) : Play.Add(path,curTime,"prev"))
PlayerPlaylist.AddHandler(
    PlayerPlaylist.queue,
    lambda (path,curTime) : Play.Add(path,curTime,"queue"))
        

class Pause(Db.Base,FileEvent):
    __tablename__ = 'evt_pause'

    curTime = Column(Integer)
    status = Column(Integer)

    def __init__(self,path,curTime,status,**kwds): 
        self.curTime = curTime
        status2db={'pause':0,'unpause':1}
        try:self.status = status2db[status]
        except KeyError:
            common.logging.error("Wrong status %s among %s" % (status,status2db.keys()))
            raise
        FileEvent.__init__(self,path,**kwds)

PlayerPlaylist.AddHandler(
    PlayerPlaylist.pause,
    lambda (path,curTime,status) : Pause.Add(path,curTime,status))


class Seek(Db.Base,FileEvent):
    __tablename__ = 'evt_seek'

    curTime = Column(Integer)
    newTime = Column(Integer)

    def __init__(self,path,curTime,newTime,**kwds): 
        self.curTime = curTime
        self.newTime = newTime
        FileEvent.__init__(self,path,**kwds)

PlayerPlaylist.AddHandler(
    PlayerPlaylist.seek,
    lambda (path,curTime,newTime) : Seek.Add(path,curTime,newTime))

