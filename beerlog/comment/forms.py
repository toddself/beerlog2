from flaskext.wtf import Form, TextAreaField, TextField
from flaskext.wtf.html5 import EmailField, IntegerField
from wtforms.validators import Length, Email, Required, ValidationError
from wtforms.widgets import HiddenInput

class EntryCommentForm(Form):
    body = TextAreaField("Comment", [Length(min=4, max=1024, message="Required")])
    posted_by_name = TextField("Name", [Length(min=4, max=128, message="Required")])
    posted_by_email = EmailField("E-Mail", [Email("Invalid e-mail address"),
                                            Required("Required")])
    entry_id = IntegerField(widget=HiddenInput())