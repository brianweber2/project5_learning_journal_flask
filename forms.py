from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, PasswordField
from wtforms.validators import (DataRequired, Email, ValidationError, Length,
                                EqualTo)
from wtfpeewee.orm import model_form

import models


class EntryForm(FlaskForm):
    """Form for adding a journal entry to the database."""
    title = StringField('Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time_spent = StringField('Time Spent', validators=[DataRequired()])
    learning = TextAreaField('What I Learned', validators=[DataRequired()])
    resources = TextAreaField(
        'Resources to Remember',
        validators=[DataRequired()
    ])
    tags = StringField(
        'Tags (seperate by a comma)',
        validators=[DataRequired()
    ])


# Model Form to update a journal entry.
EditEntryForm = model_form(models.Entry,
    field_args={
        'learning': {'label': 'What I Learned'},
        'resources': {'label': 'Resources to Remember'},
        'tags': {'label': 'Tags (seperate by a comma'}
    })


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
