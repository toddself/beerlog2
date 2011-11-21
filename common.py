from __future__ import division
from __future__ import absolute_import
from functools import wraps
from StringIO import StringIO
import hashlib
import os

from sqlobject import connectionForURI, sqlhub
from PIL import Image
from boto import connect_s3
from boto.s3.key import Key
from flask import session, flash, redirect, url_for

from blog.models import Entry, Users, Tag

def store_image(config, filename):
    extension = filename.rsplit('.', 1)[1]

    s3_image_name = "%s.%s" % (hashlib.md5(filename).hexdigest(),
                               extension)
    s3_thumb_name = "%s%s" % (hashlib.md5(filename).hexdigest(),
                              config['IMAGE_THUMBNAIL_EXT'])
    bucket = connect_to_s3(config['AWS_ACCESS_KEY'],
                           config['AWS_SECRET_KEY'],
                           config['AWS_BUCKET_NAME'])
    image_data = resize_image(filename, config['IMAGE_FULL_SIZE'])
    thumb_data = resize_image(filename,
                              config['IMAGE_THUMBNAIL_SIZE'])
    save_to_s3(image_data, bucket, s3_image_name)
    save_to_s3(thumb_data, bucket, s3_thumb_name)
    os.unlink(filename)
    flash("Success!")
    return(s3_image_name, s3_thumb_name)

def save_to_s3(data, bucket, s3_filename):
    k = Key(bucket)
    k.name = s3_filename
    k.set_contents_from_file(data, policy='public-read')
    k.set_acl('public-read')

def connect_to_s3(access_key, secret_key, bucket_name):
    conn = connect_s3(aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    bucket = conn.get_bucket(bucket_name)
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
    
def connect_db(config):
    init = False    
    if not os.path.exists(config['DB_NAME']):
        init = True
    connection = connectionForURI("%s%s%s" % (config['DB_DRIVER'], 
                                              config['DB_PROTOCOL'], 
                                              config['DB_NAME']))
    sqlhub.processConnection = connection
    if init:
        init_db(config)

def init_db(config):
    Entry.createTable()
    Users.createTable()
    Tag.createTable()
    admin = Users(email=config['ADMIN_USERNAME'])
    admin.set_pass(config['PASSWORD_SALT'], config['ADMIN_PASSWORD'])

def allowed_file(filename, ext):
    return '.' in filename and filename.rsplit('.', 1)[1] in ext