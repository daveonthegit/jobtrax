#
#   Root app — hub at /; labs under /lab8 … /lab11; JobTrax under /jobtrax.
#
#   PythonAnywhere — put this at the TOP of /var/www/…_wsgi.py (edit username/path):
#
#   import os, sys
#   MYSITE = "/home/dxiao3043/mysite"   # folder that contains flask_app.py + lab9/ + jobtrax/
#   if MYSITE not in sys.path:
#       sys.path.insert(0, MYSITE)
#   os.environ.setdefault("FLASK_SECRET_KEY", "long-random-string-here")
#   from flask_app import app as application
#
#   If imports still fail, confirm Files shows every package under the same folder as flask_app.py:
#   lab8/__init__.py lab8/app.py  lab9/__init__.py lab9/app.py  lab10/ lab11/ jobtrax/
#   (Linux is case-sensitive: JobTrax != jobtrax.)
#
#   Hub errors — TemplateNotFound home.html: use this flask_app (route "/" → index.html), not an old home().
#   BuildError lab11.home: deploy templates/index.html from this repo or pull latest; lab11.home is supported as redirect.
#   Set FLASK_SECRET_KEY in PythonAnywhere Web → Environment variables when using wsgi.py.
#
#   Each lab keeps its own folder: blueprint, templates/, mydatabase.db (where used).
#

import os
import sys

# Repo root: folder containing this file. Override if needed:
#   export MYSITE_HOME=/home/you/mysite   or set in WSGI before importing flask_app.
_SITE_ROOT = os.environ.get("MYSITE_HOME", "").strip() or os.path.dirname(os.path.abspath(__file__))
if _SITE_ROOT not in sys.path:
    sys.path.insert(0, _SITE_ROOT)

from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from lab8.app import lab8_bp
from lab9.app import lab9_bp
from lab10.app import lab10_bp
from jobtrax.app import jobtrax_bp

# PythonAnywhere: accept lab11_bp or legacy bp if lab11/app.py was renamed locally.
import lab11.app as _lab11

lab11_bp = getattr(_lab11, "lab11_bp", None) or getattr(_lab11, "bp", None)
if lab11_bp is None:
    raise ImportError(
        "lab11.app must define Blueprint as lab11_bp or bp. "
        "Upload lab11/app.py from this repo into /home/…/mysite/lab11/."
    ) from None

BASE_DIR = _SITE_ROOT

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-for-production")

# Trust X-Forwarded-* from PythonAnywhere / reverse proxies (HTTPS, host, URL building).
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

csrf = CSRFProtect(app)

app.register_blueprint(lab8_bp, url_prefix="/lab8")
app.register_blueprint(lab9_bp, url_prefix="/lab9")
app.register_blueprint(lab10_bp, url_prefix="/lab10")
app.register_blueprint(lab11_bp, url_prefix="/lab11")
app.register_blueprint(jobtrax_bp, url_prefix="/jobtrax")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "1") == "1")
