from package.Databases.database_model import User
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class CreateAccountFlaskForm(FlaskForm):
    first_name = StringField('First Name: ', validators=[DataRequired()])
    last_name = StringField('Last Name: ', validators=[DataRequired()])
    username = StringField('Username: ', validators=[DataRequired(Length(min=5, max=20))])
    email = StringField('Email: ', validators=[DataRequired(Length(max=20))])
    password = PasswordField('Password: ', validators=[DataRequired(Length(min=8, max=25))])
    confirm_password = PasswordField('Confirm Password: ', validators=[DataRequired(Length(min=8, max=25))])
    submit = SubmitField()

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already taken!')


class LoginFlaskForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateAccountFlaskForm(FlaskForm):
    add_funds = IntegerField("Add Funds: ")
    username = StringField('Update Username: ')
    email = StringField('Update Email: ')
    password = PasswordField('Update Password: ')
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already taken!')

class DeleteAccountFlaskForm(FlaskForm):
    submit = SubmitField('Delete Account')