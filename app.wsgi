import os
# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))
import sys
print (sys.path)
import bottle
# ... build or import your bottle application here ...
import index
# Do NOT use bottle.run() with mod_wsgi
application = bottle.default_app()
