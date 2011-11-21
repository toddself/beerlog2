from __future__ import division
from __future__ import absolute_import
import re

import hashlib
from datetime import datetime

from sqlobject import *
from flask import Flask

class Users(SQLObject):
    first_name = UnicodeCol(length=128, default="")
    last_name = UnicodeCol(length=128, default="")
    email = UnicodeCol(length=255)
    alias = UnicodeCol(length=255, default="")
    password = UnicodeCol(length=255, default="sdlfjskdfjskdfjsadf")
    created_on = DateTimeCol(default=datetime.now())
    last_modified = DateTimeCol(default=datetime.now())
    last_login = DateTimeCol(default=datetime.now())
    avatar = UnicodeCol(default="")
    
    def set_pass(self, salt, password_value):
        password = hashlib.sha256("%s%s" % (salt, password_value)).hexdigest()
        self._SO_set_password(password)
    
    def get_alias(self):
        return "%s %s" % (self.first_name, self.last_name)

class Entry(SQLObject):
    title = UnicodeCol(length=255)
    body = UnicodeCol()
    tags = RelatedJoin('Tag')
    slug = UnicodeCol(length=255)
    post_on = DateTimeCol(default=datetime.now())
    created_on = DateTimeCol(default=datetime.now())
    last_modified = DateTimeCol(default=datetime.now())
    draft = BoolCol(default=False)
    author = ForeignKey('Users')
    deleted = BoolCol(default=False)
    
    def _set_title(self, value):
        self._SO_set_title(value)
        self._SO_set_slug(get_slug_from_title(value))

class Tag(SQLObject):
    name = UnicodeCol(length=255)
    entries = RelatedJoin('Entry')
    
def get_slug_from_title(title):
    return re.sub('[^A-Za-z0-9-]', '', re.sub('\s','-', title)).lower()