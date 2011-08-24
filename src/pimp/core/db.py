# Db module provides an high level database access to log files and
# events. This module is a paranoid logger in order to log file
# moving, tag modification, file renaming in a transparency manner.
#
# The main table of the db is the table file. A file element is the
# path of an audio file and some informations such as type,
# modification date, duration and audio fingerprint. The File class
# permits to ask (through Get static method) the db if a file is
# already known. If the file is already known, the Get method returns
# the id of the database entry. If the path file is not known, an
# entry is created. For more information, see File.Get method
# information.
#
# The second part of the module is the events. To add an event, create
# a class that inherited FileEvent or Event.


import common
from file import format_md5,modification_date,duration

from sqlalchemy import  create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime , desc
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declared_attr, declarative_base

from datetime import datetime

# This class configures sqlalchemy database engine.
# It is used by all events to access the database.
# Method Configure MUST be called during initialisation.
class Db(object):
    Base = declarative_base()
    @staticmethod
    def Configure(user,pwd,dbName):
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
    path = Column(String(256))
    lastModDate = Column(DateTime)
    duration = Column(Integer)


    # Get a file from the db or create an entry in the db and return it.
    # An entry is added if
    # - the path is not found
    # - the modification date in db is older than modification date of the file
    @staticmethod
    def Get(path,frontend="pimp"):
        ret=Db.session.query(File).filter(File.path==path).order_by(desc(File.date)).limit(1).first()
        if ret != None:
            mdfile = modification_date(path)
            mddb = ret.lastModDate
            if mdfile > mddb:
                print "File '%s' has been modified" % path
                print "A new entry is created"
            else :
                return ret
        fm = format_md5(path)
        if fm == None :
            print "Error : format has not been found '%s'" % path
            return None
        dur = duration(path)
        if dur == None :
            print "Error : duration has not been found '%s'" % path
            return None
        f=File(path,fm[0],fm[1],dur,frontend=frontend)
        Db.session.add(f)
        Db.session.commit()
        return f

    @staticmethod
    def Find(path):
        """ Return a File object from a given path or None if it don't exist in database """
        ret=Db.session.query(File).filter(File.path==path).order_by(desc(File.date)).limit(1).first()
        return ret
        

    @staticmethod
    def All():
        return Db.session.query(File).all()
        

    def __init__(self,path,format,md5,duration,frontend):
        self.date = datetime.now()
        self.who = frontend
        self.hostname = "Unused"
        self.version = common.version
        self.zicApt = md5
        self.albumApt = "Unused"
        self.vApt = "TODO;"
        self.format = format
        self.path = path
        self.lastModDate = modification_date(path)
        self.duration = duration
        
        
    def __repr__(self):
        return "File %s, %s ,%s , %s , %s" % (self.id, self.date, self.who, self.path, self.zicApt)

# Event is the base class of the event logger engine. It contains the
# base field for all event and the static method Add used to add an
# event to db.
class Event(object):
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    frontend = Column(String(64))
    backend = Column(String(64))
    hostname = Column(String(64))
    version = Column(String(64))

# Create an event object and add it to the db. If an error occurs, it
# return None
    @classmethod
    def Add(cls,*params,**kwds):
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
    def Last(cls,number=None,til=None):
        return Db.session.query(cls).order_by(desc(cls.date)).limit(number or 100).all()

    
class FileEvent(Event):
    # For sqlalchemy
    @declared_attr
    def fileId(cls):
        return Column(Integer, ForeignKey('file.id'))
    # For sqlalchemy
    @declared_attr
    def file(cls):
        return relationship(File,primaryjoin="%s.fileId == File.id" % cls.__name__)

    @classmethod
    def FindByFile(cls,path):
        return Db.session.query(cls).join(File). filter(File.path==path).all() 

    def __init__(self,path,**kwds):
        Event.__init__(self,**kwds)
        self.file=File.Get(path)
        if self.file == None :
            raise FileError(path)
        self.fileId = self.file.id

    def __repr__(self):
        return "%s , fileid:%s , file:%s" % (Event.__repr__(self),self.fileId, self.file.path)







