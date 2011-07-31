import Pyro.core

class JokeGen(Pyro.core.ObjBase):
        def __init__(self):pass
                Pyro.core.ObjBase.__init__(self)
        def joke(self, name):
                return "Sorry "+name+", I don't know any jokes."


class Remote(object):
    def __init__(self,player1,player2):
        Pyro.core.initServer()
        daemon=Pyro.core.Daemon()
        uri=daemon.connect(player,"player")
        
        print "The daemon runs on port:",daemon.port
        print "The object's uri is:",uri
        
        daemon.requestLoop()
        


if __name__=="__main__":
    Remote(JokeGen())
