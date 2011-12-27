
import sys,os
sys.path.insert(0,os.path.abspath("./src/"))

import Pyro4
Pyro4.config.HMAC_KEY="pimp"

import pimp.core.common
import pimp.core.playlist


player=Pyro4.Proxy("PYRO:player@localhost:9998")
Note=Pyro4.Proxy("PYRO:Note@localhost:9998")          # get a Pyro proxy to the greeting object
Comment=Pyro4.Proxy("PYRO:Comment@localhost:9998")          # get a Pyro proxy to the greeting
