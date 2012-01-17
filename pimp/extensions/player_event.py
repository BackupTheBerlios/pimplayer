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



# def CountBySong(cls,path):
#     if type(path) is str:path=Path(path)
#     return Db.session.query(Play,Play.count(cls.zicApt)).filter(Play.status.like('%'+path.getPath()+'%')).group_by(cls.zicApt).all() 
# #         session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()

# class PlayerEvent(db.Db.Base):
#     __tablename__ = 'evt_player'

#     PLAYID='playid'
#     NEXT='next'
#     PREV='prev'
#     QUEUE='queue'
    
    
#     date = db.Column(db.DateTime)
#     consumedTime = db.Column(db.Integer)
#     event = db.Column(db.String(64))
    
#     @declared_attr
#     def fileId(cls):
#         return Column(Integer, ForeignKey('file.id'))
#     # For sqlalchemy
#     @declared_attr
#     def file(cls):
# #        return relationship(File,primaryjoin="%s.fileId == File.id" % cls.__name__,order_by=desc(File.date))
#         return relationship(File,primaryjoin="%s.zicApt == File.zicApt" % cls.__name__,
#                             order_by=desc(File.date),
#                             foreign_keys=File.zicApt,
#                             uselist=False,lazy='immediate')


#     def __init__(self,path,event,consumedTime): 
#         self.event=event
#         self.consumedTime = consumedTime
# #        db.FileEvent.__init__(self,path,**kwds)


#def updatePlayerEvent(date_min,date_max):


#     Play
