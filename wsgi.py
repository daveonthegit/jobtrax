# WSGI entry for PythonAnywhere and other hosts.
# In the PythonAnywhere Web tab, point the WSGI file to this module, e.g.:
#   import sys
#   sys.path.insert(0, "/home/YOUR_USERNAME/path/to/this/repo")
#   from wsgi import application
# Or keep the default /var/www/..._wsgi.py and paste the "paste this" block from flask_app.py docstring.
#
import os
import sys
MYSITE = "/home/dxiao3043/mysite"
if MYSITE not in sys.path:
    sys.path.insert(0, MYSITE)
os.environ.setdefault("FLASK_SECRET_KEY", "t0xbngPtxpM/ZY2QKc+qg63Qi0sl7kuEtJKzCHwppiM=")
from flask_app import app as application