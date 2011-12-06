import re
import hashlib
from datetime import datetime

from sqlobject import *

from beerlog.image.models import Image
from beerlog.settings import PASSWORD_SALT

class Users(SQLObject):
    first_name = UnicodeCol(length=128)
    last_name = UnicodeCol(length=128)
    email = UnicodeCol(length=255, unique=True)
    alias = UnicodeCol(length=255)
    password = UnicodeCol(length=255, default="sdlfjskdfjskdfjsadf")
    created_on = DateTimeCol(default=datetime.now())
    last_modified = DateTimeCol(default=datetime.now())
    last_login = DateTimeCol(default=datetime.now())
    avatar = ForeignKey("Image", notNone=False, default=None)
    active = BoolCol(default=True)
    admin = BoolCol(default=False)
    
    def set_pass(self, salt, password_value):
        password = hashlib.sha256("%s%s" % (salt, password_value)).hexdigest()
        self._SO_set_password(password)

def generate_password(cleartext):
    cyphertext = hashlib.sha256("%s%s" % (PASSWORD_SALT, cleartext))
    return cyphertext.hexdigest()        