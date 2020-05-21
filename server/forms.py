from flask_wtf import FlaskForm
from wtforms import MultipleFileField, PasswordField, StringField
from wtforms.validators import InputRequired, EqualTo, Email, Length

class VerifyForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired('Please Input Something')])