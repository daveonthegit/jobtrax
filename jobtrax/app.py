#
#   JobTrax — Smart Job Tracker (see Jobtrax/docs)
#

from flask import session

from .blueprint import jobtrax_bp
from .db import init_db
from .forms import LogoutForm

init_db()


@jobtrax_bp.context_processor
def inject_logout():
    if session.get("user_id"):
        return {"logout_form": LogoutForm()}
    return {}


from . import routes_applications  # noqa: E402
from . import routes_auth  # noqa: E402
from . import routes_companies  # noqa: E402
from . import routes_dashboard  # noqa: E402
from . import routes_parser  # noqa: E402

if __name__ == "__main__":
    from flask import Flask

    _app = Flask(__name__)
    _app.secret_key = "dev"
    _app.register_blueprint(jobtrax_bp, url_prefix="/jobtrax")
    _app.run(debug=True)
