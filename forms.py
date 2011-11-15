from __future__ import division
from __future__ import absolute_import

from sqlobject import SQLObjectNotFound

from models import Users
from wtforms import Form, TextField, TextAreaField, \
                    BooleanField, HiddenField, validators
from wtforms.ext.dateutil.fields import DateTimeField

def is_valid_user(form, field):
    try:
        Users.get(field.data)
    except SQLObjectNotFound:
        raise validators.ValidationError("Not a valid user")

class PostForm(Form):
    title = TextField('Title', [validators.Length(min=1, max=255, message="You must provide a title")])
    post = HiddenField('Post', [validators.Length(min=4, max=1048576, message="Cat got your tongue?")])
    post_on = DateTimeField('Post On', display_format="%Y-%m-%d %H:%M")
    is_draft = BooleanField("Draft")
    