# saved as greeting.py
import Pyro4
import pimp.extensions.tag


class Remote(object):
	def __init__(self,player,port):
            print "Running Pyro4 remote object access ..."
            Pyro4.config.HMAC_KEY="pimp"
            daemon = Pyro4.Daemon(port=port)
            uri_player = daemon.register(player,"player")
            uri_Note = daemon.register(pimp.extensions.tag.Note,"Note")
            uri_Comment = daemon.register(pimp.extensions.tag.Comment,"Comment")
            print "[Pyro4] Object player at uri =", uri_player , uri_Note , uri_Comment      # print the uri so we can use it in the client l		daemon.requestLoop()
            daemon.requestLoop()                  # start the event loop of the server to wait for calls


