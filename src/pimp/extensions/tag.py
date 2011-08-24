""" This module permits to log comments and notes associated to a
file.

Because they inherits :class:`FileEvent`, you can use methods from it.

"""
import pimp.core.db as db
from pimp.core.pimp import player

class Note(db.Db.Base,db.FileEvent):
    """ To log a note on a file"""
    __tablename__ = 'note'

    xnote = db.Column(db.Integer)

    def __init__(self,path,note,**kwds): 
        self.xnote = note
        db.FileEvent.__init__(self,path,**kwds)

    def __repr__(self):
        return db.FileEvent.__repr__(self) + " " + str(self.xnote)
        
    @staticmethod
    def OnPLayedFile(note):
        """ Permit to note the currently played file """
        return Note.Add(player.current().path,note)


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
    def OnPLayedFile(text):
        """ Permit to comment the currently played file """
        return Comment.Add(player.current().path,text)
