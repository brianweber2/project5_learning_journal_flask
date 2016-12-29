from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField

from wtfpeewee.orm import model_form

import models


class AddEntryForm(FlaskForm):
    """Form for adding a journal entry to the database."""
    title = StringField('Title', validators=[DataRequired()])
    date = DateField('DatePicker', format='%Y-%m-%d',
        validators=[DataRequired()])
    time = IntegerField('Time Spent (mins)', validators=[DataRequired()])
    notes = TextAreaField('What did you learn?', validators=[DataRequired()])
    resources = TextAreaField('Resources to Remember',
        validators=[DataRequired()])


EditEntryForm = model_form(models.Entry,
    exclude=[],
    field_args={

    })
