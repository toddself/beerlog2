from __future__ import division
from __future__ import absolute_import

from flaskext.wtf import Form, FileField, file_required, IntegerField,\
                         TextField, validators

class ImageForm(Form):
    img_msg = 'You have to provide a file to upload'
    image = FileField(u'Image', validators=[file_required(message=img_msg)])
    width = IntegerField("Width", validators=[validators.Optional()])
    height = IntegerField('Height', validators=[validators.Optional()])
    caption = TextField('Caption', validators=[validators.Optional()])