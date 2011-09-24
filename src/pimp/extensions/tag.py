""" This module permits to log comments and notes associated to a
file.

Because they inherits :class:`FileEvent`, you can use methods from it.

"""
import pimp.core.db as db
from pimp.core.pimp import player

class Note(db.Db.Base,db.FileEvent):
    """ To log a note on a file.

    Some examples::

    >>> Note.Add(player.current(),4)
    >>> player.sort(key=Note.GetNote,reverse=True)
    
    """
    __tablename__ = 'note'

    xnote = db.Column(db.Integer)

    def __init__(self,path,note,**kwds): 
        self.xnote = note
        db.FileEvent.__init__(self,path,**kwds)

    def __repr__(self):
        return db.FileEvent.__repr__(self) + " " + str(self.xnote)

    @staticmethod
    def GetNote(path):
        try:
            ns=Note.FindBySong(path)
            return sum([a.xnote for a in ns]) / len(ns)
        except ZeroDivisionError: return None
        
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
    def GetComments(path): return [c.text for c in Comment.FindBySong(path)]
