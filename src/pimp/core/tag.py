""" This module permits to log comments and notes associated to a
file.

Because they inherits :class:`FileEvent`, you can use methods from it.

"""
from db import FileEvent , Column, Integer, Db, String
from pimp import player


class Note(Db.Base,FileEvent):
    """ To log a note on a file"""
    __tablename__ = 'note'

    xnote = Column(Integer)

    def __init__(self,path,note,**kwds): 
        self.xnote = note
        FileEvent.__init__(self,path,**kwds)

    def __repr__(self):
        return FileEvent.__repr__(self) + " " + str(self.xnote)
        
    @staticmethod
    def OnPLayedFile(note):
        """ Permit to note the currently played file """
        return Note.Add(player.getCurrent().path,note)


class Comment(Db.Base,FileEvent):
    """ To log a comment on a file"""
    __tablename__ = 'comment'

    text = Column(String(512))

    def __init__(self,path,text,**kwds): 
        self.text = text
        FileEvent.__init__(self,path,**kwds)

    def __repr__(self):
        return FileEvent.__repr__(self) + " " + self.text

    @staticmethod
    def OnPLayedFile(text):
        """ Permit to comment the currently played file """
        return Comment.Add(player.getCurrent().path,text)
