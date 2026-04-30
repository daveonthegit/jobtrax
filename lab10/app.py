from flask import Blueprint, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

lab10_bp = Blueprint(
    "lab10",
    __name__,
    template_folder="templates",
)


class NameForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


@lab10_bp.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        return redirect(url_for("lab10.success", name=name))
    return render_template("form.html", form=form)


@lab10_bp.route("/success/<name>")
def success(name):
    return f"{name} was the name submitted."


if __name__ == "__main__":
    from flask import Flask

    _app = Flask(__name__)
    _app.config["SECRET_KEY"] = "Secret Key"
    _app.register_blueprint(lab10_bp)
    _app.run(debug=True)
