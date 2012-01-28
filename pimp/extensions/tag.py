""" This module permits to log comments and notes associated to a
file.

Because they inherits :class:`FileEvent`, you can use methods from it.


Some examples::

    >>> Note.Add(player.current(),4)
    >>> player.sort(key=Note.GetNote,reverse=True)
    >>> Comment.Add(player.current(),"cool")
    >>> Comment.FindBySong(player.current())

"""
import pimp.core.db as db
from pimp.core.pimp import player

class Note(db.Db.Base,db.FileEvent):
    """ To log a note on a file."""
    __tablename__ = 'note'

    xnote = db.Column(db.Integer)

    def __init__(self,path,note,**kwds): 
        self.xnote = note
        db.FileEvent.__init__(self,path,**kwds)

#    def __repr__(self):
#        return db.FileEvent.__repr__(self) + " " + str(self.xnote)

    @staticmethod
    def GetNote(path):
        """ Compute the notes average of audio fingerprint associated
        to this path """
        try:
            ns=Note.FindBySong(path)
            return sum([a.xnote for a in ns]) / len(ns)
        except ZeroDivisionError: return None

    @staticmethod
    def GreatherOrEqualThan(note):
        """ Get a """
#        return db.Db.session.query(Note.zicApt,Note.xnote).filter("xnote>=%d" % note).distinct().all()
        return db.Db.session.query(Note).filter("xnote>=%d" % note).group_by(Note.zicApt).all()
#select file.path,avg(xnote)  from (select * from file order by date desc) as file,note where file.zicApt=note.zicApt group by note.zicApt

class Comment(db.Db.Base,db.FileEvent):
    """ To log a comment on a file"""
    __tablename__ = 'comment'

    text = db.Column(db.String(512))

    def __init__(self,path,text,**kwds): 
        self.text = text
        db.FileEvent.__init__(self,path,**kwds)

    def __repr__(self):
        return db.FileEvent.__repr__(self) + " " + self.text

    @staticmethod
    def GetComments(comment): 
        """ Return comments (use FindBySong) """ 
        return [c.text for c in Comment.FindBySong(path)]

    @staticmethod
    def Find(comment):
        return db.Db.session.query(Comment).filter(Comment.text.like('%'+comment+'%')).group_by(Comment.zicApt).all()
