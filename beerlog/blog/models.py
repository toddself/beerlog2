from __future__ import division
from __future__ import absolute_import
import re

from datetime import datetime

from sqlobject import *

class Entry(SQLObject):
    title = UnicodeCol(length=255)
    body = UnicodeCol()
    tags = RelatedJoin('Tag')
    slug = UnicodeCol(length=255, default="")
    post_on = DateTimeCol(default=datetime.now())
    created_on = DateTimeCol(default=datetime.now())
    last_modified = DateTimeCol(default=datetime.now())
    draft = BoolCol(default=False)
    author = ForeignKey('Users')
    deleted = BoolCol(default=False)
    comments = RelatedJoin('Comment')
    
    def _set_title(self, value):
        self._SO_set_title(value)
        self._SO_set_slug(get_slug_from_title(value))
        
    def _get_comment_count(self):
        return len(self.comments)

class Tag(SQLObject):
    name = UnicodeCol(length=255)
    entries = RelatedJoin('Entry')    
    
def get_slug_from_title(title):
    return re.sub('[^A-Za-z0-9-]', '', re.sub('\s','-', title)).lower()