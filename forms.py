from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, PasswordField
from wtforms.validators import (DataRequired, Email, ValidationError, Length,
                                EqualTo)
from wtfpeewee.orm import model_form

import models


class EntryForm(FlaskForm):
    """Form for adding a journal entry to the database."""
    title = StringField(validators=[DataRequired()])
    date = DateField(validators=[DataRequired()])
    time_spent = StringField(validators=[DataRequired()])
    learning = TextAreaField(validators=[DataRequired()])
    resources = TextAreaField(validators=[DataRequired()])


# Model Form to update a journal entry.
EditEntryForm = model_form(models.Entry)


def email_exists(form, field):
    if models.User.select().where(models.User.email == field.data).exists():
        raise ValidationError("User with that email already exists.")


class RegistrationForm(FlaskForm):
    """Form for registering a new user."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()])


class LoginForm(FlaskForm):
    """Form for logging in user."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
