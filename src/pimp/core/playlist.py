from common import *
from file import duration,supported
#from db import File
import os.path

logger=logging.getLogger("playlist")
logger.setLevel(logging.INFO)
	
class VersionnedList(list):
	""" A VersionnedList is a list where all mutation methods
	increase a list version number. This permits to know if the
	list has been modified

	TODO : Find a more elegant way to do that ?
	"""
	__version=0

	def version(self): return self.__version

	def pop(self,idx):
		self.__version+=1
		return list.pop(self,idx)
		
	def append(self,item):
		self.__version+=1
		return list.append(self,item)
		
	def __setitem__(self,*args):
		self.__version+=1
		return list.__setitem__(self,*args)

	def __delitem__(self,*args):
		self.__version+=1
		return list.__delitem__(self,*args)

	def __setslice__(self,*args):
		self.__version+=1
		return list.__setslice__(self,*args)

	def __getslice__(self,*args):
		return VersionnedList(list.__getslice__(self,*args))

	def __delslice__(self,*args):
		self.__version+=1
		return list.__delslice__(self,*args)

	def sort(self,*args,**kwargs):
		self.__version+=1
		return list.sort(self,*args,**kwargs)

	def __str__(self):
		acc=""
		for i in self:
			acc+=str(i)+"\n"
		return acc

class Playlist(VersionnedList,object):
	""" A Playlist is a circular buffer of :class:`song`. A
	:class:`song` must have a path attribute. When a song can not
	be created, it raises a FileNotSupported.

	When the playlist is modified, playlist :data:`version` is
	increased (Should be implemented in :mod:`mpd`) See VersionnedList.

	All get* method return a playlistItem. These method have a
	setCurrent parameter to consume the playlist."""

	def __init__(self,cls_song,paths=[]):
		self.cls_song=cls_song
		for e in paths: self.appendByPath(e)
		self.__current = 0

	def appendByPath(self,path):
		""" Append a song to the playlist.
		Increase playlist version."""
		try :
			self.append(self.cls_song(path))
			logger.info("Song Added %s" % path)
		except FileNotSupported:pass

	def current(self,**kwargs):
		""" Return current song. 'kwargs' is unsed. (t's just
		here for homogenieity with setCurrent in getNext and
		other method) """
		return self.__getitem__(self.__current)

        def information(self):
		""" Return inforamtion about playlist ..."""
		try :
			current=[('currentPath', self.current().path),
				 ('currentId' , self.current().id ),
				 ('currentPos',self.__current)]
		except : current = []
		return Info([('length',len(self)),('version',self.version())]
			    +current)

	def __getStep(self,step,setCurrent=False):
		try :
			tmpCurrent = (self.__current + step) % len(self)
			ret = self.__getitem__(tmpCurrent)
			if setCurrent:
				self.__current = tmpCurrent
			return ret
		except : raise
	def getNext(self,setCurrent=False):
		return self.__getStep(1,setCurrent=setCurrent)

	def getPrev(self,setCurrent=False):
		return self.__getStep(-1,setCurrent=setCurrent)
	def get(self,idx,setCurrent=False): 
		ret = self[idx]
		if setCurrent:
			self.__current = idx
		return ret
			

	# To make playlist a serializable object
	# --------------------------------------
	def __getstate__(self):
		""" Implementation of serialization methods """
		return {"current" : self.__current,
			"playlist" : self._playlist}
	def __setstate__(self,state):
		""" Implementation of deserialization methods """
		self.__current=state["current"]
		self._playlist=state["playlist"]


	def getCurrentIdx(self): return self.__current


	# Pretty print of the playlist.
	# context can be use to print a part of the playlist arround the current song.
	def show(self,context=None):
		i=0
		if len(self) == 0:
			print "Playlist is empty"
			return None
		print " Pos | Path"
		if context:
			for i in range(-context,0):
				print "%s%4s | %s" % (" ",(self.__current+i) % len(self),os.path.split(self.__getStep(i).path)[1])
			print "%s%4s | %s" % (">",self.__current,os.path.split(self.__getStep(0).path)[1])
			for i in range(1,context+1):
				print "%s%4s | %s" % (" ",(self.__current+i) % len(self),os.path.split(self.__getStep(i).path)[1])
		else:
			for e in self:
				if e == self.current():
					cur=">"
				else: cur=" "
				print "%s%4s | %s" % (cur,i,os.path.split(e.path)[1])
				i+=1

	def move(self,src,dest):
		""" Move a song for position src to position dest"""
		try :
			if src >= dest:
				self.insert(dest,self.pop(src))
			else :
				self.insert(dest,self[src])
				self.pop(src)
		except IndexError: return None

	

