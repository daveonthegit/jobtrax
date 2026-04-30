from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Optional, Regexp

_EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Regexp(_EMAIL_RE, message="Enter a valid email address."),
        ],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class CompanyForm(FlaskForm):
    company_name = StringField("Company name", validators=[DataRequired()])
    industry = StringField("Industry", validators=[Optional()])
    location = StringField("Location", validators=[Optional()])
    website = StringField("Website", validators=[Optional()])
    submit = SubmitField("Save")


class ApplicationForm(FlaskForm):
    company_id = SelectField("Company", coerce=int, validators=[DataRequired()])
    status_id = SelectField("Status", coerce=int, validators=[DataRequired()])
    job_title = StringField("Job title", validators=[DataRequired()])
    location = StringField("Role location", validators=[Optional()])
    job_type = StringField("Job type", validators=[Optional()])
    salary_range = StringField("Salary", validators=[Optional()])
    application_date = DateField("Application date", validators=[Optional()])
    deadline = DateField("Deadline", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Save")


class ApplicationEditForm(FlaskForm):
    job_title = StringField("Job title", validators=[DataRequired()])
    location = StringField("Role location", validators=[Optional()])
    job_type = StringField("Job type", validators=[Optional()])
    salary_range = StringField("Salary", validators=[Optional()])
    application_date = DateField("Application date", validators=[Optional()])
    deadline = DateField("Deadline", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Save")


class StatusChangeForm(FlaskForm):
    status_id = SelectField("New status", coerce=int, validators=[DataRequired()])
    note = StringField("Note (optional)", validators=[Optional()])
    submit = SubmitField("Update status")


class ContactForm(FlaskForm):
    contact_name = StringField("Name", validators=[Optional()])
    contact_role = StringField("Role", validators=[Optional()])
    email = StringField("Email", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional()])
    submit = SubmitField("Save")


class ParserPasteForm(FlaskForm):
    input_type = SelectField(
        "Input type",
        choices=[("job_listing", "Job listing"), ("email", "Email paste")],
        validators=[DataRequired()],
    )
    raw_text = TextAreaField("Paste text here", validators=[DataRequired()])
    submit = SubmitField("Preview parse")


class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")


class LogoutForm(FlaskForm):
    submit = SubmitField("Log out")


class ParserConfirmForm(FlaskForm):
    company_name = StringField("Company", validators=[DataRequired()])
    job_title = StringField("Job title", validators=[DataRequired()])
    location = StringField("Location", validators=[Optional()])
    job_type = StringField("Job type", validators=[Optional()])
    salary_range = StringField("Salary range", validators=[Optional()])
    deadline = StringField("Deadline", validators=[Optional()])
    status_id = SelectField("Status", coerce=int, validators=[DataRequired()])
    contact_name = StringField("Contact name", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Confirm and save")
