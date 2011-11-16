from __future__ import division
from __future__ import absolute_import

import hashlib
import os
from datetime import datetime
from functools import wraps
from StringIO import StringIO

from flask import Flask, request, session, redirect, url_for, \
    render_template, flash
from sqlobject import connectionForURI, sqlhub, AND
from werkzeug import secure_filename
from PIL import Image
from boto import connect_s3
from boto.s3.key import Key

from models import Entry, Users, Tag
from forms import PostForm

app = Flask(__name__)
app.config.from_envvar('BEERLOG_SETTINGS')

if app.config['DB_DRIVER'] == 'sqlite':
    app.config['DB_NAME'] = os.path.join(os.getcwd(), app.config['DB_NAME'])
    app.config['DB_PROTOCOL'] = '://'

def require_auth(callback):
    @wraps(callback)
    def auth(*args, **kwargs):
        if session.get('logged_in'):
            return callback(*args, **kwargs)
        else:
            flash("You must be authenicated to access this section")
            return redirect(url_for('show_entries'))
    return auth

def connect_db():
    init = False    
    if not os.path.exists(app.config['DB_NAME']):
        init = True

    connection = connectionForURI("%s%s%s" % (app.config['DB_DRIVER'], 
                                              app.config['DB_PROTOCOL'], 
                                              app.config['DB_NAME']))
    sqlhub.processConnection = connection
    
    if init:
        init_db()

def init_db():
    Entry.createTable()
    Users.createTable()
    Tag.createTable()
    admin = Users(email=app.config['ADMIN_USERNAME'])
    admin.set_pass(app.config['PASSWORD_SALT'], app.config['ADMIN_PASSWORD'])
    
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

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
    thumb_size = [0,0]
    max_l = im.size.index(max(im.size))
    min_l = im.size.index(min(im.size))
    thumb_size[max_l] = int(t_m_l)
    thumb_size[min_l] = int(round((t_m_l / im.size[max_l]) * im.size[min_l]))
    im.thumbnail(thumb_size, Image.ANTIALIAS)
    thumb = StringIO()
    im.save(thumb, 'JPEG')
    return thumb

@app.before_request
def before_request():
    connect_db()

@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def show_entries():
    entries = Entry.select(Entry.q.draft==False).orderBy("-post_on")
    return render_template('show_entries.html', entries=entries)

@app.route('/upload', methods=['POST', 'GET'])
@require_auth
def upload_image():
    if request.method == 'POST':
        fn = request.files['file']
        if fn and allowed_file(fn.filename):
            filename = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], 
                      secure_filename(fn.filename))
            try:
                os.stat(app.config['TEMP_UPLOAD_FOLDER'])
            except OSError:
                os.makedirs(app.config['TEMP_UPLOAD_FOLDER'])
            fn.save(filename)                      
            extension = filename.rsplit('.', 1)            
            s3_image_name = "%s.%s" % (hashlib.md5(filename).hexdigest(), 
                                       extension)
            s3_thumb_name = "%s%s" % (hashlib.md5(filename).hexdigest(), 
                                      app.config['IMAGE_THUMBNAIL_EXT'])                  
            bucket = connect_to_s3(app.config['AWS_ACCESS_KEY'],
                                   app.config['AWS_SECRET_KEY'],
                                   app.config['AWS_BUCKET_NAME'])
            image_data = resize_image(filename, app.config['IMAGE_FULL_SIZE'])
            thumb_data = resize_image(filename, 
                                      app.config['IMAGE_THUMBNAIL_SIZE'])
            save_to_s3(image_data, bucket, s3_image_name)
            save_to_s3(thumb_data, bucket, s3_thumb_name)
            os.unlink(filename)
            return render_template('upload_file.html', 
                                    data={'thumb': s3_thumb_name, 
                                          'img': s3_image_name})
        else:
            return render_template('upload_file.html', data={'thumb': "error", 'img': "error'"})
    else:
        return render_template('upload_file.html')

@app.route('/add', methods=['POST', 'GET'])
@require_auth
def add_entry():
    post = PostForm(request.form)    
    if request.method == 'POST' and post.validate():
        entry = Entry(title=post.title.data,
                      body=post.post.data,
                      author=session.get('user_id'),
                      post_on=post.post_on.data)
        flash("New entry was sucessfully added")
        return redirect(url_for('show_entries'))
    else:
        return render_template('add_entry.html', 
                               data={'form': post, 'date': datetime.now()})


@app.route('/admin')
@require_auth
def admin():
    if not session.get('logged_in'):
        flash("You must be logged in")
        return redirect(url_for('add_entry'))
    else:
        pass

# login and logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        pclear = request.form['password']
        key = app.config['PASSWORD_SALT']
        pcrypt = hashlib.sha256("%s%s" % (key, pclear)).hexdigest()
        u_req = Users.select(
            AND(
                Users.q.email==request.form['username'],
                Users.q.password==pcrypt
                )
            )

        if not list(u_req):
            error = 'Invalid username'
        else:
            session['logged_in'] = True
            session['user_id'] = u_req[0].id
            flash('You were logged in')
            return redirect(url_for('show_entries'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()