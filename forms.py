from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)], description="Username")
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)], description="Password")


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)], description="Your Username")
    email = StringField('Email', validators=[InputRequired(), Email(message="Invalid email")], description="example@example.com")
    password = PasswordField(
                'Password', 
                validators=[
                    InputRequired(),
                    Length(min=6, max=80), 
                    EqualTo('confirm', message='Passwords must match')
                ],
                description="Make it secure"
            )
    confirm = PasswordField('Confirm', validators=[InputRequired(), Length(min=6, max=80)], description="Confirm Your Password")
