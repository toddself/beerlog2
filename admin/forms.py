from __future__ import division
from __future__ import absolute_import

from sqlobject import SQLObjectNotFound

from flaskext.wtf import Form, TextField, HiddenField, PasswordField
from wtforms.validators import Length, Optional, Email, Required, EqualTo
from flaskext.wtf.html5 import URLField, IntegerField, EmailField
from wtforms.widgets import HiddenInput
                         
from wtforms.ext.dateutil.fields import DateTimeField

class UserForm(Form):
    first_name = TextField('First Name',
                           [Length(max=128, message="128 character max"),
                           Required(message="You must provide a first name")])
    last_name = TextField('First Name',
                          [Length(max=128, message="128 character max"),
                          Required(message="You must provide a last name")])
    email = EmailField('E-Mail', 
                        [Email('Invalid e-mail address'),
                        Required(message="You must provide an e-mail address")])
    alias = TextField('Alias',
                      [Length(max=255, message="255 character max"),
                      Optional()])
    avatar = URLField("Avatar", [Optional()])
    user_id = IntegerField(widget=HiddenInput())
    
class LoginForm(Form):
    email = EmailField("Username",
                       [Email("Invalid e-mail address"),
                       Required(message="You must provide a username")])
    password = PasswordField("Password",
                             [Required(message="You must provide a password")])
                             
class ChangePasswordForm(Form):
    password = PasswordField("Password",
                             [Required(message="You must supply a password"),
                             EqualTo('password2', message="Passwords must match"),
                             Length(max=255, message="255 character max")])
    password2 = PasswordField("Verify Password",
                              [Required(message="You must verify your password")])
    user_id = IntegerField(widget=HiddenInput())