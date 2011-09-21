"""Db module provides an high level database access to log files and
events. This module is a paranoid logger in order to log file moving,
tag modification, file renaming in a transparency manner.

The main table of the db is the table file. A file element is the path
of an audio file and some informations such as type, modification
date, duration and audio fingerprint. The File class permits to ask
(through Get static method) the db if a file is already known. If the
file is already known, the Get method returns the id of the database
entry. If the path file is not known, an entry is created. For more
information, see File.Get method information.

To create an new event, create a class that inherited FileEvent or Event.

All method attributes 'path' must implement getPath() method. Path class is a string wrapper.

"""


import common
from file import format_md5,modification_date,duration

from sqlalchemy import  create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime , desc
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declared_attr, declarative_base

from datetime import datetime

class Path(str):
    """ A default Path class implementation. Use it to add a string
    path to the database. """
    def getPath(self): return self

class Db(object):
    """This class configures sqlalchemy database engine.
    It is used by all events to access the database.
    Method Configure MUST be called during initialisation."""
    Base = declarative_base()
    @staticmethod
    def Configure(user,pwd,dbName):
        """ Called to initialize database module """
        Db.engine=create_engine("mysql://%s:%s@localhost/%s" % (user,pwd,dbName), use_ansiquotes=True)
        Db.session = sessionmaker(bind=Db.engine)()
        Db.Base.metadata.create_all(Db.engine)

# Use to manage file error ... shity -> TODO.
class FileError(Exception):
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return repr("FileError on '%s'" % self.path)


class File(Db.Base):
    """ File Table """
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    who = Column(String(64))
    hostname = Column(String(64))
    version = Column(String(64))
    zicApt = Column(String(32))
    albumApt = Column(String(32))
    vApt = Column(String(64))
    format = Column(String(16))
    path = Column(String(1024))
    lastModDate = Column(DateTime)
    duration = Column(Integer)


    @staticmethod
    def Get(path,frontend="pimp"):
        """Get a file from the db or create an entry in the db and return it.
        An entry is added if:
        
        * the path is not found
        * the modification date in db is older than modification date of the file

        """
        ret=Db.session.query(File).filter(File.path==path.getPath()).order_by(desc(File.date)).limit(1).first()
        if ret != None:
            mdfile = modification_date(path.getPath())
            mddb = ret.lastModDate
            if mdfile > mddb:
                print "File '%s' has been modified" % path.getPath()
                print "A new entry is created"
            else :
                return ret
        fm = format_md5(path.getPath())
        if fm == None :
            print "Error : format has not been found '%s'" % path.getPath()
            return None
        dur = duration(path.getPath())
        if dur == None :
            print "Error : duration has not been found '%s'" % path.getPath()
            return None
        f=File(path,fm[0],fm[1],dur,frontend=frontend)
        Db.session.add(f)
        Db.session.commit()
        return f

    @staticmethod
    def Find(path):
        """ Return a File object from a given path or None if it don't exist in database """
        ret=Db.session.query(File).filter(File.path==path.getPath()).order_by(desc(File.date)).limit(1).first()
        return ret
        

    @staticmethod
    def All():
        """ Return all file row """
        return Db.session.query(File).all()

    @staticmethod
    def Lasts(number=None):
        """ Return 'number' lasts events or 100 lasts events if number is None """ 
        return Db.session.query(File).order_by(desc(File.date)).limit(number or 100).all()

        

    def __init__(self,path,format,md5,duration,frontend):
        self.date = datetime.now()
        self.who = frontend
        self.hostname = "Unused"
        self.version = common.version
        self.zicApt = md5
        self.albumApt = "Unused"
        self.vApt = "TODO;"
        self.format = format
        self.path = path.getPath()
        self.lastModDate = modification_date(path.getPath())
        self.duration = duration
        
        
    def __repr__(self):
        return "File %s, %s ,%s , %s , %s" % (self.id, self.date, self.who, self.path, self.zicApt)

class Event(object):
    """Event is the base class of the event logger engine. It contains the
    base field for all event and the static method Add used to add an
    event to db."""
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    frontend = Column(String(64))
    backend = Column(String(64))
    hostname = Column(String(64))
    version = Column(String(64))

    @classmethod
    def Add(cls,*params,**kwds):
        """Create an event object and add it to the db. If an error
        occurs, it return None"""
        try: a=cls(*params,**kwds)
        except FileError as e: 
            common.logging.info(e)
            return None
        except TypeError as e: 
            common.logging.error("%s : %s " % (cls.__name__,e))
            return None
        Db.session.add(a)
        Db.session.commit()
        common.logging.info("%s" % a)
        return a
        
    def __init__(self,frontend="pimp"):
        self.date = datetime.now()
        self.frontend = frontend
        self.backend = "unspecified"
        self.hostname = "unspecified"
        self.version = "Version TODO"
        
    def __repr__(self):
        return "%s id:%s" % (self.__class__.__name__,self.id)

    @classmethod
    def Lasts(cls,number=None,til=None):
        """ Return 'number' lasts events or 100 lasts events if number is None """ 
        return Db.session.query(cls).order_by(desc(cls.date)).limit(number or 100).all()

    @classmethod
    def All(cls):
        return Db.session.query(cls).all()
    
class FileEvent(Event):
    """ A fileEvent is an event on a file.  
    All method attributes 'path' must implement getPath method.
    """
    # For sqlalchemy
    @declared_attr
    def fileId(cls):
        return Column(Integer, ForeignKey('file.id'))
    # For sqlalchemy
    @declared_attr
    def file(cls):
        return relationship(File,primaryjoin="%s.fileId == File.id" % cls.__name__)

    @classmethod
    def FindByPath(cls,path):
        """ Find all cls events for a given path """
        return Db.session.query(cls).join(File). filter(File.path==path.getPath()).all() 

    def __init__(self,path,**kwds):
        Event.__init__(self,**kwds)
        self.file=File.Get(path)
        if self.file == None :
            raise FileError(path)
        self.fileId = self.file.id

    def __repr__(self):
        return "%s , fileid:%s , file:%s" % (Event.__repr__(self),self.fileId, self.file.path)







