from __future__ import division
from __future__ import absolute_import
from datetime import datetime

from sqlobject import *

class Image(SQLObject):
    url = UnicodeCol(unique=True)
    height = IntCol()
    width = IntCol()
    caption = UnicodeCol(default="")
    created_on = DateTimeCol(default=datetime.now())
    
    def thumb_size(self, width=0, height=0):
        if width:
            return self.thumb_height(width)
        else:
            return self.thumb_width(height)
    
    def thumb_height(self, width):
        ratio = float(75) / float(self.width)
        raw_height = float(self.height) * ratio
        return int(round(raw_height))
    
    def thumb_width(self, height):
        ratio = float(75) / float(self.height)
        raw_width = float(self.width) * ratio
        return int(round(raw_width))