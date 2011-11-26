from StringIO import StringIO
import hashlib
import os

from PIL import Image
from boto import connect_s3
from boto.s3.key import Key
from flask import render_template, request
from werkzeug import secure_filename

from image.forms import ImageForm
from settings import *

def list_images():
    bucket = connect_to_s3()    
    images = [key.name for key in bucket.list()]
    return render_template('upload_file.html', data={'images': images,
                                                     'filename': ""})
    
def create_image():
    image_form = ImageForm(request.form) 
    if request.method == 'POST' and image_form.validate():
        filename = os.path.join(TEMP_UPLOAD_FOLDER,
                                secure_filename(request.files['file'].filename))
        try:
            os.stat(TEMP_UPLOAD_FOLDER)
        except OSError:
            os.makedirs(TEMP_UPLOAD_FOLDER)
        fn.save(filename)
        image = store_image(filename)
        return render_template('upload_file.html',
                                data={'filename': image,
                                      'images': None})
    else:
        return render_template('upload_file.html')

def delete_image(key):
    bucket = connect_to_s3()
    k = bucket.get_key(key)
    if k:
        k.delete()

def store_image(filename):
    extension = filename.rsplit('.', 1)[1]
    s3_image_name = "%s.%s" % (hashlib.md5(filename).hexdigest(),
                               extension)
    bucket = connect_to_s3()
    image_data = resize_image(filename, IMAGE_FULL_SIZE)
    save_data(image_data, bucket, s3_image_name)
    os.unlink(filename)
    flash("Image %s uploaded" % s3_image_name)
    return s3_image_name

def save_data(data, bucket, s3_filename):
    k = Key(bucket)
    k.name = s3_filename
    k.set_contents_from_file(data, policy='public-read')
    k.set_acl('public-read')

def connect_to_s3():
    conn = connect_s3(aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    bucket = conn.get_bucket(AWS_BUCKET_NAME)
    return bucket

def resize_image(filename, t_m_l):
    im = Image.open(filename)
    if max(im.size) < 800:
        image = StringIO()
        return image
    else:
        thumb_size = [0,0]
        max_l = im.size.index(max(im.size))
        min_l = im.size.index(min(im.size))
        thumb_size[max_l] = int(t_m_l)
        thumb_size[min_l] = int(round((t_m_l / im.size[max_l]) * im.size[min_l]))
        im.thumbnail(thumb_size, Image.ANTIALIAS)
        thumb = StringIO()
        im.save(thumb, 'JPEG')
        return thumb