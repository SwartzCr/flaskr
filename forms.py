from flask import session
from flask_wtf import FlaskForm
from wtforms.csrf.session import SessionCSRF
from wtforms import StringField, BooleanField, Form, validators, RadioField

class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = 'CSRF_SECRET_KEY'

    @property
    def csrf_context(self):
        return session

class LoginForm(BaseForm):
    username = StringField('Username:', [validators.Length(min=4, max=50), validators.InputRequired()])
    password = StringField('Password:', [validators.Length(min=4), validators.InputRequired()])

class SignupForm(LoginForm):
    public = BooleanField('public', default=False)

class Remove(BaseForm):
    pass

class CommentSubmit(BaseForm):
    title = StringField('Title:', [validators.InputRequired()])
    text = StringField('Text:', [validators.InputRequired()])
    tags = RadioField("Tags:")

