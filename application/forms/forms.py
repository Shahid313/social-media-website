from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,SelectField,FileField,TextAreaField
from wtforms.validators import DataRequired,Email,Length,InputRequired
from application.models.models import *
from flask_wtf.file import FileField, FileAllowed, FileRequired

class LoginForm(FlaskForm):
	username = StringField('Username',validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('Password',validators=[InputRequired(), Length(min=8, max=80)])
	submit = SubmitField('Login')

class SignupForm(FlaskForm):
	email = StringField('email',validators=[InputRequired(), Email(message = 'Invalid email'), Length(max=50)])
	username = StringField('Username',validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('Password',validators=[InputRequired(), Length(min=8, max=80)])
	user_image = FileField('Image', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
	submit = SubmitField('Sign Up')

class UpdateSignupForm(FlaskForm):
	email = StringField('email',validators=[InputRequired(), Email(message = 'Invalid email'), Length(max=50)])
	username = StringField('Username',validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('Password',validators=[InputRequired(), Length(min=8, max=80)])
	user_image = FileField('Image', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
	submit = SubmitField('Update')

class MessageForm(FlaskForm):
    message = TextAreaField(('Message'), validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Send')