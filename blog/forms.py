from __future__ import division
from __future__ import absolute_import

from sqlobject import SQLObjectNotFound

from wtforms import Form, TextField, TextAreaField, BooleanField, validators
from wtforms.ext.dateutil.fields import DateTimeField

class EntryForm(Form):
    title = TextField('Title', [validators.Length(min=1, max=255, message="You must provide a title")])
    body = TextAreaField('Body', [validators.Length(min=4, max=1048576, message="The body is required")])
    time = DateTimeField('Time', display_format="%H:%M")
    date = DateTimeField('Date', display_format="%m/%d/%Y")
    is_draft = BooleanField('Draft?')
    is_deleted = BooleanField('Delete?')
    