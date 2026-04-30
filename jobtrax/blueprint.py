from flask import Blueprint

jobtrax_bp = Blueprint(
    "jobtrax",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/jobtrax/static",
)
