from __future__ import division
from __future__ import absolute_import

from sqlobject import SQLObjectNotFound

from models import Users
from wtforms import Form, TextField, TextAreaField, DateTimeField,\
                    BooleanField, validators
from wtforms.widgets import HiddenInput

def is_valid_user(form, field):
    try:
        Users.get(field.data)
    except SQLObjectNotFound:
        raise validators.ValidationError("Not a valid user")

class EntryForm(Form):
    title = TextField('Title', [validators.Length(min=1, max=255, message="You must provide a title")])
    post = TextAreaField('Post', [validators.Length(min=4, max=1048576, message="Cat got your tongue?")], widget=HiddenInput())
    post_on = DateTimeField('Post On', format="%Y-%m-%d %H:%M", widget=HiddenInput())
    is_draft = BooleanField('Draft')
    