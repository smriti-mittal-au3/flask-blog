from flask_wtf import Form
from wtforms import validators, StringField, PasswordField
from wtforms.fields.html5 import EmailField

class RegisterForm(Form):
	fullname = StringField('Full Name', [validators.Required()])
	email = EmailField('Email Id', [validators.Required()])
	username = StringField('Username', [validators.Required(), validators.Length(min=3,max=25)])
	password = PasswordField('New Password', [
				validators.Required(),
				validators.EqualTo('confirm', message='passwords must match'),
				validators.Length(min=3,max=25)
				])
	confirm = PasswordField('Confirm Password')
	

class LoginForm(Form):
	username = StringField('Username', [
							validators.Required(),
							validators.Length(min=3,max=25)
							])
	password = PasswordField('Password', [
							validators.Required(),
							validators.Length(min=3,max=25)
							])

