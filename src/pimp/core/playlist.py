from common import *
from file import duration,supported
from db import File
import os.path


class Playlist:
	""" A Playlist is a circular buffer of :class:`song`. A
	:class:`song` must have a path attribute. When a song can not
	be created, it raises a FileNotSupported.

	When the playlist is modified, playlist :data:`version` is
	increased (Should be implemented in :mod:`mpd`).

	All get* method return a playlistItem. These method have a
	setCurrent parameter to consume the playlist."""

	version=0
	""" Increased when the playlist is modified."""
	
	def __init__(self,cls_song,paths=[]):
		self.cls_song=cls_song
		self._playlist=[]

		if paths==None : paths = []
		self.appends(paths)
		self.current = 0
		self.init = True # Hack to have the first element on the first 'getNext()' call
		self.version=0


	def appends(self,paths): 
		""" Call many time self.append then increase many time playlist version !"""
		for e in paths: self.append(e)


	def move(self,src,dest):
		""" Move a song for position src to position dest"""
		try :
			e = self._playlist[src]
			self._playlist[src] = None
			self._playlist.insert(dest+1,e)
			self._playlist.remove(None)
			self.version=self.version+1
		except IndexError: return None

	def moveById(self,idx,dest):
		pos=0
		for e in self._playlist:
			if e.id==idx: break 
			pos=pos+1
		self.move(pos,dest)
						


	def getById(self,idx,setCurrent=False):
		""" Get a song from his id (should be implemented in :mod:`mpd`) """
		pos=0
		for p in self._playlist:
			if p.id==idx : 
				if setCurrent : self.current=pos
				return p
			pos=pos+1
		return None

	def __getitem__(self,idx):return self.getByPos(idx)
	def __setitem__(self,idx,path):
		""" Append a song to the playlist.
		Increase playlist version."""
		self._playlist.append("iop")
	
		try :
			s=self.cls_song(path)
			self._playlist.append(s)
			self.version=self.version+1
		except FileNotSupported:pass


	def append(self,path):
		""" Append a song to the playlist.
		Increase playlist version."""
		try :
			s=self.cls_song(path)
			self._playlist.append(s)
			self.version=self.version+1
		except FileNotSupported:pass
			
	
	def getByPos(self,pos,setCurrent=False):
		""" Get a song from his position """
		if self._playlist == []:
			print "Playlist empty"
			return None
		elif abs(pos) >= len(self._playlist):
			print "Idx out of bound"
			return None
		else:
			elt=self._playlist[pos]
			if setCurrent : self.current=pos
			return elt
                
        def information(self):
		""" Return inforamtion about playlist ..."""
		return Info([('length',len(self._playlist)),('version',self.version)]
			    +(
				self.getCurrent() != None 
				and(
					[('currentPath', self.getCurrent().path),
					 ('currentId' , self.getCurrent().id ),
					 ('currentPos',self.current)])
				or [])
			    )

		

		
	def __getStep(self,step,setCurrent=False):
		if self._playlist == [] : return None
		return self.getByPos( (self.current+step) % len(self._playlist) ,setCurrent=setCurrent)

	def getStep(self,step,setCurrent=False):
		return self.__getStep(step,setCurrent=setCurrent)

	
	def getCurrent(self,setCurrent=False):
		"""Return the current song item"""
		return self.__getStep(0)

	# # Return the current song's Index
	# # DEPRECATED: Use getCurrent().id instead !
	# def getCurrentId(self):
	# 	if self._playlist == [] : return None
	# 	return self._playlist[self.current].id

	def getCurrentPos(self):
		if self._playlist == [] : return None
		return self.current


	# Increase playlist version
	def remove(self,idx):
		self._playlist.pop(idx)
		self.version=self.version+1

	# Call remove
	def removeId(self,idx):
		pos=0
		for e in self._playlist:
			if e.id==idx : 
				self.remove(pos)
				return None
			pos=pos+1


	# Increase playlist version
	def clear(self):
		del self._playlist[:]
		self.current=0
		self.version=self.version+1


	def getNext(self,setCurrent=False):
		return self.__getStep(1,setCurrent=setCurrent)

	def getPrev(self,setCurrent=False):
		return self.__getStep(-1,setCurrent=setCurrent)

        def length(self):
            return len(self._playlist)

	# Should return [PlaylistItem] instead of [path :: String] 
	def getPlaylist(self):
		def snd(a): return a[1]
		return map(snd,self._playlist)

	# Pretty print of the playlist.
	# context can be use to print a part of the playlist arround the current song.
	def show(self,context=None):
		i=0
		if self._playlist==[]: 
			print "Playlist is empty"
			return None
		print " Pos | Path"
		if context:
			for i in range(-context,0):
				print "%s%4s | %s" % (" ",(self.getCurrentPos()+i) % self.length(),os.path.split(self.__getStep(i).path)[1])
			print "%s%4s | %s" % (">",self.getCurrentPos(),os.path.split(self.__getStep(0).path)[1])
			for i in range(1,context+1):
				print "%s%4s | %s" % (" ",(self.getCurrentPos()+i) % self.length(),os.path.split(self.__getStep(i).path)[1])
				
		else:
			for e in self._playlist:
				if self.getByPos(i) == self.getCurrent():
					cur=">"
				else: cur=" "
				print "%s%4s | %s" % (cur,i,os.path.split(e.path)[1])
				i=i+1

	def mapOnPath(self,fct):
		return [i for i in (fct(i.path) for i in self._playlist) if i]
