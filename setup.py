from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
#files = ["src/"]

import sys,os
sys.path.insert(0,os.path.abspath("./src/"))
import pimp.core.common

setup(name = "pimp",
      version = pimp.core.common.version,
      description = "python player framework",
      author = "dal",
      author_email = "kedals0@gmail.com",
#      url = "whatever",
      #Name the folder where your packages live:
          #(If you have other packages (dirs) or modules (py files) then
      #put them into the package directory - they will be found 
      #recursively.)
      packages = ['pimp/'],
#      package_dir={"pimp": "src/"}
      #'package' package must contain files (see list above)
      #I called the package 'package' thus cleverly confusing the whole issue...
      #This dict maps the package name =to=> directories
      #It says, package *needs* these files.
#      package_data = {'pimp' : ['src/'] },
      #'runner' is in the root.
      #    scripts = ["runner"],
      long_description = """ """ 
      #
      #This next part it for the Cheese Shop, look a little down the page.
      #classifiers = []     
      ) 
