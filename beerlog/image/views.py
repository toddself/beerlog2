from datetime import datetime
from StringIO import StringIO
import hashlib
import os
from urlparse import urlparse

from PIL import Image as PIL_Image
from boto import connect_s3
from boto.s3.key import Key
from flask import render_template, request, flash, redirect, url_for
from werkzeug import secure_filename

from beerlog.image.forms import ImageForm
from beerlog.image.models import Image
from beerlog.settings import *
from beerlog.admin.views import require_auth

@app.route('/image/')
@require_auth
def list_images():
    images = list(Image.select())
    return render_template('show_images.html', data={'images': images})

@app.route('/image/add/', methods=['GET','POST'])
@require_auth
def create_image():
    image_form = ImageForm(request.form) 
    if image_form.validate_on_submit():
        fn = image_form.image.file.filename
        width = image_form.width.data
        height = image_form.height.data
        caption = image_form.caption.data
        if '.' in fn and fn.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            filename = os.path.join(TEMP_UPLOAD_FOLDER,
                                    secure_filename(fn))
            mime = image_form.image.file.content_type
            try:
                os.stat(TEMP_UPLOAD_FOLDER)
            except OSError:
                os.makedirs(TEMP_UPLOAD_FOLDER)
            image_form.image.file.save(filename)
            
            if width and not height:
                long_side = int(width)
            elif height and not width:
                long_side = int(height)
            elif width and height:
                if width >= height:
                    long_side = int(width)
                else:
                    long_side = int(height)
            else:
                long_side = IMAGE_FULL_SIZE
            
            image, thumb_size = store_image(filename, mime, long_side)
            if image:
                os.unlink(filename)
                url = "%s/%s" % (IMAGE_BASEPATH, image)
                img = Image(url=url, 
                            width=thumb_size[0], 
                            height=thumb_size[1],
                            caption=caption)
                flash("Image uploaded!")
            else:
                flash("Couldn't store the image in S3. Please try again.")
            return render_template('upload_file.html',
                                    data={'filename': url,
                                          'form': image_form})
        else:
            return render_template('upload_file.html',
                                   data={'form': image_form})
    else:
        
        return render_template('upload_file.html',
                               data={'form': image_form})

@app.route('/image/<image_id>/delete/')
@require_auth
def delete_image(image_id):
    img = Image.get(image_id)
    key = urlparse(img.url).path.rsplit('/', 1)[1]
    bucket = connect_to_s3()
    k = bucket.get_key(key)
    if k:
        k.delete()
        Image.delete(img.id)
        flash("%s was deleted from S3 and the database.  It is unrecoverable." % key)
        return redirect(url_for('list_entries'))

def store_image(filename, mime, long_side):
    extension = filename.rsplit('.', 1)[1]
    uploadtime = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M')
    s3_image_name = "%s%s.%s" % (uploadtime,
                                 hashlib.md5(filename).hexdigest(),
                                 extension)
    bucket = connect_to_s3()
    image_data, thumb_size = resize_image(filename, long_side)
    save_data(image_data, bucket, s3_image_name, mime)
    return s3_image_name, thumb_size

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
    if max(im.size) < t_m_l:
        image = StringIO()
        return image, im.size
    else:
        thumb_size = [0,0]
        max_l = im.size.index(max(im.size))
        min_l = im.size.index(min(im.size))
        thumb_size[max_l] = int(t_m_l)
        ratio = float(t_m_l) / float(im.size[max_l])
        raw_min_l = ratio * float(im.size[min_l])
        thumb_size[min_l] = int(round(raw_min_l))
        im.thumbnail(thumb_size, PIL_Image.ANTIALIAS)
        thumb = StringIO()
        im.save(thumb, 'JPEG')
        return thumb, thumb_size