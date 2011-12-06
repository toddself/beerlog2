from __future__ import division
from __future__ import absolute_import

from flaskext.wtf import Form, FileField, file_required, IntegerField,\
                         TextField, validators, SelectField

class ImageForm(Form):
    img_msg = 'You have to provide a file to upload'
    image = FileField(u'Image', validators=[file_required(message=img_msg)])
    side = SelectField("Resize side", choices=[('', ''),('0', 'Width'), ('1', 'Height')])
    resize_to = IntegerField('Resize to', validators=[validators.Optional()])
    caption = TextField('Caption', validators=[validators.Optional()])