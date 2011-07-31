#!/usr/bin/env python

import sys, os, time, thread , threading
import glib, gobject
import pygst
pygst.require("0.10")
import gst

from common  import Info,logging #,Guard
#from playlist import * 

class Player:
	"""Player is a simple audio player based on pygst. It's just
	able to play a file and do some basic operation on it such as
	:func:`seek` ...

	Player can be initialised with a filepath which is loaded.  This
	permits to be able to obtain some informations about this file. 
		
	Use :func:`load` to load a song in order to ask some information about a file.
		
	This player class is not safe. A method is invoked but the action is
	not necessary done. For instance, the stop method sucessed even if
	the player is currently stopped.
	
	To avoid leaking (socket, thread), :func:`stop` method MUST BE explicitly used.

	_ready is an threading.Event to wait the change of the gst status (don't tested ...)

	TODO: The player should have a queue song to manage crossfading.
	"""
	def __init__(self,filepath=None):
		""" Player status is set to stop """
		self.player = gst.element_factory_make("playbin2", "player")
		fakesink = gst.element_factory_make("fakesink", "fakesink")
		alsasink = gst.element_factory_make("alsasink", "alsasink")
		self.player.set_property("video-sink", fakesink)
		self.player.set_property("audio-sink", alsasink)
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus_handler_id=self.bus.connect("message", self._on_message)
		thread.start_new_thread(self._startMainloop, ())
		self._ready=threading.Event()
		if filepath != None :
			self.load(filepath)

	def quit(self):
		"""Stop player, stop loop, clean bus"""
		logging.debug("Quit player")
		self.stop()
		self.bus.disconnect(self.bus_handler_id)
		try:self.loop.quit()
		except:pass
		
	# To launch the glib mainloop (manage events/messages)
	def _startMainloop(self):
		self.loop = glib.MainLoop()
		gobject.threads_init()
		self.loop.run()



	def _on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			logging.debug("pygst: End of File")
			self.queue()
		elif t == gst.MESSAGE_ERROR:
			self.player.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			self.handle_error()
			logging.debug("pygst error: %s | %s" % (err, debug))
		elif t == gst.MESSAGE_STATE_CHANGED:
			if message.src is self.player:
				old, new, pending = message.parse_state_changed()
				if new==gst.STATE_READY:
					self._ready.set()
				if new==gst.STATE_NULL:
					self._ready.clear()


	def seek(self,t):
		"""Seek the current song to t seconds

		:param t: Seek time in seconds
		"""
		self.player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, t * 1000000000)

	def information(self):
		""" To get some information about the loaded file.
		:func:`load` has to called before."""
		common={'volume':self.volume(),
			'mute':self.player.get_property("mute")}
		state=self.player.get_state()[1]
		if state == gst.STATE_PLAYING or state == gst.STATE_PAUSED:
			if state == gst.STATE_PLAYING: status="play"
			if state == gst.STATE_PAUSED: status="pause"
			infos={'status':status,
			       'duration':self.player.query_duration(gst.FORMAT_TIME, None)[0] / 1000000000,
			       'position':self.player.query_position(gst.FORMAT_TIME, None)[0] / 1000000000,
			       'volume':self.volume(),
			       'mute':self.player.get_property("mute"),
			       'gstPlayedFile':self.player.get_property("uri")
			       }
		else: 
			infos={'status':"stop"}
		return Info(common.items() + infos.items())

	def status(self):
		""" Get the player status

		:rtype: 'play' | 'pause' | 'stop'"""
		state=self.player.get_state()[1]
		if state == gst.STATE_PLAYING : return "play"
		elif state == gst.STATE_PAUSED: return "pause"
		else : return "stop"

	def currentSong(self):
		""" Ask to pygst the current played song """

		if self.player.get_state()[1] == gst.STATE_PLAYING:
			return self.player.get_property("uri")
		else : return "No song played"


	def load(self,filepath):
		""" Load a file in pygst to get some informations (duration ...).

		:rtype: False if:

		* the file type can not be determined 
		* the file doesnt exist
		* the player is playing """
		if filepath != None and os.path.isfile(filepath):
			if self.player.get_state()[1] == gst.STATE_PLAYING:
				return False
			else:
				self.player.set_property("uri", "file://" + filepath)
				s=self.player.set_state(gst.STATE_PLAYING)
				if s ==  gst.STATE_CHANGE_FAILURE:
					logging.debug("File can not be loaded %s" % filepath)
					return False
				s=self.player.set_state(gst.STATE_PAUSED)
				self._ready.wait()
				return True
		else: return False
			
	def play(self,filepath):
		""" Call :func:`stop`, then :func:`load`. Finally, the gstreamer status is set to PLAY.
		
		:rtype: The return value of :func:`load`.
		"""

		self.stop()
		if self.load(filepath):
			self.player.set_state(gst.STATE_PLAYING)
			logging.debug("Play %s" % filepath)
			return True
		else: 
			logging.debug("File '%s' can not be played" % filepath)
			return False
		
	def stop(self):
		""" To stop a played file. This method is not safe """
		self.player.set_state(gst.STATE_NULL)

	# Should use "about-signal". See TODO
	def queue(self):
		pass

	# This method is called when gstreamer emits an error.
	def handle_error(self): pass

	def pause(self):
		""" Toogle the status between play and pause status """
		if self.status()=='play' : 
			self.player.set_state(gst.STATE_PAUSED)
		elif self.status()=='pause':
			self.player.set_state(gst.STATE_PLAYING)

	
	def volume(self,v=None):
		""" Change the volume. If v is None, just return the
		volume.
		
		:type: v belongs to [0,1]
		:rtype: the current volume"""
		if v !=None:
			self.player.set_property("volume",v)
		return self.player.get_property("volume")

	def mute(self,m=None):
		""" Set mute to m.

		:rtype: the mute state (boolean). """
		m1 = self.player.get_property("mute")
		if m != None:
			self.player.set_property("mute",m)
			m1=m
		return m1

	def toggleMute(self):
		""" Toggle mute """
		self.mute(not self.mute())

	def __repr__(self):
		return "volume : %d" % self.volume()


