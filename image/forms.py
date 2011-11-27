from __future__ import division
from __future__ import absolute_import

from flaskext.wtf import Form, FileField, file_required

class ImageForm(Form):
    image = FileField(u'Image', validators=[file_required(message='You have to provide a file to upload')])