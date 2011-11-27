from __future__ import division
from __future__ import absolute_import

from wtforms import Form, FileField, validators, ValidationError

from settings import ALLOWED_EXTENSIONS

def allowed_file(form, field):
    if not '.' in field.data and not field.data('.', 1)[1] in ALLOWED_EXTENSIONS:
        raise ValidationError('File must be one of %s' % ", ".join(ALLOWED_EXTENSIONS))
    
class ImageForm(Form):
    image = FileField(u'Image', [allowed_file])