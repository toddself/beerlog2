from __future__ import division
from __future__ import absolute_import
from datetime import datetime

from sqlobject import *

class Image(SQLObject):
    url = UnicodeCol()
    created_on = DateTimeCol(default=datetime.now())