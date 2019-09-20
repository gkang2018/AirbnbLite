from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from database import DatabaseConnection


db = DatabaseConnection()

class RegistrationForm(FlaskForm): 

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    accountType = SelectField("Account Type", choices=[("vendor", "Vendor"), ("renter", "Property Renter")])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validateUsername(self, username): 
        user = db.findOne("users", {"username": username.data})
        if user: 
            raise ValidationError("That username is taken")
    def validateEmail(self, email): 
        email = db.findOne("users", {"email": email.data})
        if email: 
            raise ValidationError("That email is already taken")

class LoginForm(FlaskForm): 
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Login")