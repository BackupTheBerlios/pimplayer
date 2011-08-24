"""This module defines some FileEvent and attach them to player
method. For instance, when PlayerPlaylist.stop is called, Stop.Add
method is executed"""
import pimp.core.db as db
from pimp.core.pimp import PlayerPlaylist

class Stop(db.Db.Base,db.FileEvent):
    __tablename__ = 'evt_stop'

    curTime = db.Column(db.Integer)

    def __init__(self,path,curTime,**kwds): 
        db.FileEvent.__init__(self,path,**kwds)
        self.curTime = curTime

PlayerPlaylist.AddHandler(
    PlayerPlaylist.stop,
    lambda (path,curTime) : Stop.Add(path,curTime))


class Play(db.Db.Base,db.FileEvent):
    PLAYID=0
    NEXT=1
    PREV=2
    QUEUE=3
    __tablename__ = 'evt_play'

    curTime = db.Column(db.Integer)
    status = db.Column(db.Integer)

    def __init__(self,path,curTime,status,**kwds): 
        self.curTime = curTime
        status2db={'playid':Play.PLAYID,'next':Play.NEXT,'prev':Play.PREV,'queue':Play.QUEUE}
        try:self.status = status2db[status]
        except KeyError:
            common.logging.error("Wrong status %s among %s" % (status,status2db.keys()))
            raise
            
        db.FileEvent.__init__(self,path,**kwds)

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
        

class Pause(db.Db.Base,db.FileEvent):
    __tablename__ = 'evt_pause'

    curTime = db.Column(db.Integer)
    status = db.Column(db.Integer)

    def __init__(self,path,curTime,status,**kwds): 
        self.curTime = curTime
        status2db={'pause':0,'unpause':1}
        try:self.status = status2db[status]
        except KeyError:
            common.logging.error("Wrong status %s among %s" % (status,status2db.keys()))
            raise
        db.FileEvent.__init__(self,path,**kwds)

PlayerPlaylist.AddHandler(
    PlayerPlaylist.pause,
    lambda (path,curTime,status) : Pause.Add(path,curTime,status))


class Seek(db.Db.Base,db.FileEvent):
    __tablename__ = 'evt_seek'

    curTime = db.Column(db.Integer)
    newTime = db.Column(db.Integer)

    def __init__(self,path,curTime,newTime,**kwds): 
        self.curTime = curTime
        self.newTime = newTime
        db.FileEvent.__init__(self,path,**kwds)

PlayerPlaylist.AddHandler(
    PlayerPlaylist.seek,
    lambda (path,curTime,newTime) : Seek.Add(path,curTime,newTime))

