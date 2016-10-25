from flask import session
from wtforms.csrf.session import SessionCSRF
from wtforms import StringField, BooleanField, Form, validators, RadioField

class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        #TODO figure out how this works and why its not working?
        csrf_secret = 'CSRF_SECRET_KEY'

    @property
    def csrf_context(self):
        return session

class LoginForm(BaseForm):
    username = StringField('Username:', [validators.Length(min=4, max=50), validators.InputRequired()])
    password = StringField('Password:', [validators.Length(min=4), validators.InputRequired()])

class SignupForm(LoginForm):
    public = BooleanField('public', default=False)

#class FilterBy(Form):

class CommentSubmit(BaseForm):
    title = StringField('title', [validators.InputRequired()])
    text = StringField('text', [validators.InputRequired()])
    #TODO figure out how to include radio buttons as taken from the database
    tags = RadioField("Tags:")

