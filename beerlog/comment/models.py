from datetime import datetime

from sqlobject import *

class Comment(SQLObject):
    body = UnicodeCol()
    posted_by_name = UnicodeCol(length=128)
    posted_by_email = UnicodeCol(length=255)
    posted_on = DateTimeCol(default=datetime.now())
    ip_address = UnicodeCol(length=15)
    entry = RelatedJoin('Entry')