from datetime import datetime
from StringIO import StringIO
import hashlib
import os

from PIL import Image as PIL_Image
from boto import connect_s3
from boto.s3.key import Key
from flask import render_template, request, flash
from werkzeug import secure_filename

from image.forms import ImageForm
from image.models import Image
from settings import *

def list_images():
    images = Image.select()
    image_form = ImageForm()
    return render_template('upload_file.html', data={'images': images,
                                                     'filename': "",
                                                     'form': image_form})
    
def create_image():
    image_form = ImageForm(request.form) 
    if image_form.validate_on_submit():
        fn = image_form.image.file.filename
        if '.' in fn and fn.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            filename = os.path.join(TEMP_UPLOAD_FOLDER,
                                    secure_filename(fn))
            mime = image_form.image.file.content_type
            try:
                os.stat(TEMP_UPLOAD_FOLDER)
            except OSError:
                os.makedirs(TEMP_UPLOAD_FOLDER)
            image_form.image.file.save(filename)
            image = store_image(filename, mime)
            if image:
                os.unlink(filename)
                url = "%s/%s" % (IMAGE_BASEPATH, image)
                img = Image(url=url)
                flash("Image uploaded!")
            else:
                flash("Couldn't store the image in S3. Please try again.")
            return render_template('upload_file.html',
                                    data={'filename': url,
                                          'images': Image.select(),
                                          'form': image_form})
        else:
            return render_template('upload_file.html', data={'form': image_form,
                                                             'images': Image.select()})
    else:
        
        return render_template('upload_file.html', data={'images': Image.select(),
                                                         'form': image_form})

def delete_image(key):
    bucket = connect_to_s3()
    k = bucket.get_key(key)
    if k:
        k.delete()

def store_image(filename, mime):
    extension = filename.rsplit('.', 1)[1]
    uploadtime = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M')
    s3_image_name = "%s%s.%s" % (uploadtime,
                                 hashlib.md5(filename).hexdigest(),
                                 extension)
    bucket = connect_to_s3()
    image_data = resize_image(filename, IMAGE_FULL_SIZE)
    save_data(image_data, bucket, s3_image_name, mime)
    return s3_image_name

def save_data(data, bucket, s3_filename, mime):
    k = Key(bucket)
    k.name = s3_filename
    k.set_metadata('Content-Type', mime)
    k.set_contents_from_file(data, policy='public-read')
    k.set_acl('public-read')

def connect_to_s3():
    conn = connect_s3(aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    bucket = conn.get_bucket(AWS_BUCKET_NAME)
    return bucket

def resize_image(filename, t_m_l):
    im = PIL_Image.open(filename)
    if max(im.size) < IMAGE_FULL_SIZE:
        image = StringIO()
        return image
    else:
        thumb_size = [0,0]
        max_l = im.size.index(max(im.size))
        min_l = im.size.index(min(im.size))
        thumb_size[max_l] = int(t_m_l)
        thumb_size[min_l] = int(round((t_m_l / im.size[max_l]) * im.size[min_l]))
        im.thumbnail(thumb_size, PIL_Image.ANTIALIAS)
        thumb = StringIO()
        im.save(thumb, 'JPEG')
        return thumb