from common import *
from file import duration,supported
from db import File
import os.path

class Song(object):
	""" A Song has an id which is unique. This is used by
	remote client to have a remote song identifier.

	"""

	#Used to generate song ID
	Offset=0
        
	def __init__(self,filepath):
		if not supported(filepath):
			raise FileNotSupported(filepath)
		self.__filepath=filepath
		self.id=Song.Offset
		self.duration=duration(filepath)
		Song.Offset=Song.Offset+1
		self._dbfile=None
		self.__iscurrent=False
		self.update()


	def __repr__(self):
		return "%4s | %4ss | %s" % (self.id,datetime.timedelta(seconds=self.duration),self.__filepath)

	def getPath(self):
		return self.__filepath

	def isCurrent(self,s=None):
		""" Is this song is the current played song. Can be
		set with s boolean argument. """ 
		if s==True:
			self.__iscurrent=True
		elif s==False:
			self.__iscurrent=False
		return self.__iscurrent


	def show(self,pathToStr=lambda x : x):
		return "%4s | %4s | %s" % (self.duration,pathToStr(self.__filepath),self.id)

	def update(self):
		"""To find information from db. Because an song is
		added to the db when it is played, information can
		be not available when a playlist is loaded. It is
		then necessary to update it sometime."""
		try:pass
#			self._dbfile=File.Find(self,limit=1)[0]
		except: logging.debug("update exception raise ...")
