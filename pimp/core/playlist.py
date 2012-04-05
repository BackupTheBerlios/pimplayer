import common
import os.path
import os
import random

logger=common.logging.getLogger("playlist")
logger.setLevel(common.logging.INFO)
	
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
	be added, it raises a FileNotSupported.

	When the playlist is modified, playlist :data:`version` is
	increased (Should be implemented in :mod:`mpd`) See VersionnedList.

	All get* method return a playlistItem. These method have a
	setCurrent parameter to consume the playlist."""

	def __init__(self,cls_song,paths=[]):
		self.cls_song=cls_song
		for e in paths: self.appendByPath(e)
		self.__current = (0,0) 
		""" (version,idx) """
		self.__random = False
	
	def appendByPath(self,path):
		""" Append a directory recursylvely or a song to the
		playlist."""		
		if os.path.isfile(path):
			try :
				return self.appendSong(path)
			except common.FileNotSupported:raise
		for root,dirs,files in os.walk(path):
			for f in files:
				try :
					self.appendSong(root+"/"+f)
				except common.FileNotSupported:pass

	def appendSong(self,path):
		""" Append a song to the playlist.
		Increase playlist version."""
		try :
			self.append(self.cls_song(path))
			logger.info("Song Added %s" % path)
		except common.FileNotSupported:raise

	def current(self,**kwargs):
		""" Return current song. 'kwargs' is unsed. (t's just
		here for homogenieity with setCurrent in getNext and
		other method) """
		try :
			return self.__getitem__(self.currentIdx())
		except IndexError:
			raise common.NoFileLoaded()

	def isEmpty(self): return len(self)==0

        def information(self):
		""" Return inforamtion about playlist ..."""
		if not self.isEmpty() and self.current() != None:
			current=[('currentPath', self.current().getPath()),
				 ('currentId' , self.current().id ),
				 ('currentPos',self.currentIdx())]
		else:
			logger.debug("Playlist is empty")
			current = []
		return common.Info([('length',len(self)),('version',self.version())]
			    +current)

	def __getStep(self,step,setCurrent=False):
		""" Jump in playlist with a modulo """
		if self.random():
			step=random.randint(1,len(self)-1)
		tmpCurrent = (self.currentIdx() + step) % len(self)
		ret = self.get(tmpCurrent,setCurrent)
		return ret
	def getNext(self,setCurrent=False):
		""" if setCurrent is set to True, the current song
		becomes next song, otherwise it just return the next
		song """
		return self.__getStep(1,setCurrent=setCurrent)

	def getPrev(self,setCurrent=False):
		""" See getNext documentation """
		return self.__getStep(-1,setCurrent=setCurrent)
	def get(self,idx,setCurrent=False): 
		ret = self[idx]
		if setCurrent:
			self.current().isCurrent(False)
			self.__current = (self.version(),idx)
			self[idx].isCurrent(True)
		return ret

	def getCurrentIdx(self): return self.currentIdx()
	""" Deprecated: use currentIdx"""

	def currentIdx(self): 
		""" Return current played song index. Detect playlist
		modifications. """
		if self.version() != self.__current[0]:
			if not self[self.__current[1]].isCurrent():
				for i in range(0,len(self)):
					if self[i].isCurrent():
						self.__current=(self.version(),i)
		return self.__current[1]

	def move(self,src,dest):
		""" Move a song for position src to position dest"""
		try :
			if src >= dest:
				self.insert(dest,self.pop(src))
			else :
				self.insert(dest+1,self[src])
				self.pop(src)
		except IndexError: return None
		
	def random(self,state=None):
		"if state is not set, it just return current random state "
		if state != None:
			self.__random=state
		return self.__random
		
			

	# To make playlist a serializable object
	# --------------------------------------
	def __getstate__(self):
		""" Implementation of serialization methods """
		return {"current" : self.__current,
			"playlist" : self[:]}
	def __setstate__(self,state):
		""" Implementation of deserialization methods """
		del (self[:])
		for i in state["playlist"]:
			self.append(i)
		self.__current=state["current"]




	# Pretty print of the playlist.
	# context can be use to print a part of the playlist arround the current song.
	def show(self,context=None):
		i=0
		ret=""
		if len(self) == 0:
			ret+= "Playlist is empty"
			return ret
		ret+= " Pos | Path\n"
		if context:
			for i in range(-context,0):
				ret += "%s%4s | %s\n" % (" ",(self.__current+i) % len(self),os.path.split(self.__getStep(i).getPath())[1])
			print "%s%4s | %s" % (">",self.__current,os.path.split(self.__getStep(0).getPath())[1])
			for i in range(1,context+1):
				ret += "%s%4s | %s\n" % (" ",(self.__current+i) % len(self),os.path.split(self.__getStep(i).getPath())[1])
		else:
			for e in self:
				if e == self.current():
					cur=">"
				else: cur=" "
				ret += "%s%4s | %s\n" % (cur,i,os.path.split(e.getPath())[1])
				i+=1

		return ret
	

