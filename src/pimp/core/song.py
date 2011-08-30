from common import *
from file import duration,supported
from db import File
import os.path

class Song(object):
	""" A Song has an id which is unique. This is used by
	remote client to have a remote song identifier.

	song.__repr__() return the path of a song. This permit to use a song or a filepath in all database methods.

	song.__str__() return a string for printing.
	"""

	#Used to generate playlist ID
	Offset=0
        
	def __init__(self,path):
            if not supported(path):
                raise FileNotSupported(path)
            self.path=path
            self.id=Song.Offset
            self.duration=duration(path)
            Song.Offset=Song.Offset+1
            self._dbfile=None
            self.update()


	def __repr__(self):
		return "%4s | %4ss | %s" % (self.id,datetime.timedelta(seconds=self.duration),self.path)

	def getPath(self):
		return self.path

	def show(self,pathToStr=lambda x : x):
		return "%4s | %4s | %s" % (self.duration,pathToStr(self.path),self.id)

	def update(self):
		"""To find information from db. Because an song is
		added to the db when it is played, information can
		be not available when a playlist is loaded. It is
		then necessary to update it sometime."""
		try:
			self._dbfile=File.Find(self.path)
		except: logging.debug("update exception raise ...")
