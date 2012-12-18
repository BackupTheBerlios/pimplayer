"""This module defines some FileEvent and attach them to player
method. For instance, when PlayerPlaylist.stop is called, Stop.Add
method is executed"""
import audiodb.model.player as e
from pimp.core.pimp import PlayerPlaylist

PlayerPlaylist.AddHandler(
    PlayerPlaylist.stop,
    lambda (path,curTime) : e.Stop.Add(path,curTime))


PlayerPlaylist.AddHandler(
    PlayerPlaylist.play,
    lambda (path,curTime) : e.Play.Add(path,curTime,"playid"))
PlayerPlaylist.AddHandler(
    PlayerPlaylist.next,
    lambda (path,curTime) : e.Play.Add(path,curTime,"next"))
PlayerPlaylist.AddHandler(
    PlayerPlaylist.prev,
    lambda (path,curTime) : e.Play.Add(path,curTime,"prev"))
PlayerPlaylist.AddHandler(
    PlayerPlaylist.queue,
    lambda (path,curTime) : e.Play.Add(path,curTime,"queue"))
        

PlayerPlaylist.AddHandler(
    PlayerPlaylist.pause,
    lambda (path,curTime,status) : e.Pause.Add(path,curTime,status))

PlayerPlaylist.AddHandler(
    PlayerPlaylist.seek,
    lambda (path,curTime,newTime) : e.Seek.Add(path,curTime,newTime))



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
