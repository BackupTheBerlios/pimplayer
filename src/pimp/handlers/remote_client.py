import Pyro.core

# you have to change the URI below to match your own host/port.
player = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/player")

print player.joke("Irmen")
