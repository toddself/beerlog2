from __future__ import division
from __future__ import absolute_import
import hashlib
import os
from datetime import datetime

from flask import Flask, request, session, redirect, url_for, \
    render_template, flash
from sqlobject import AND
from werkzeug import secure_filename

from models import Entry, Users, Tag
from forms import PostForm
from utils import *

app = Flask(__name__)
app.config.from_envvar('BEERLOG_SETTINGS')

if app.config['DB_DRIVER'] == 'sqlite':
    app.config['DB_NAME'] = os.path.join(os.getcwd(), app.config['DB_NAME'])
    app.config['DB_PROTOCOL'] = '://'

@app.before_request
def before_request():
    connect_db(app.config)

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
        if fn and allowed_file(fn.filename, app.config['ALLOWED_EXTENSIONS']):
            filename = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], 
                      secure_filename(fn.filename))
            try:
                os.stat(app.config['TEMP_UPLOAD_FOLDER'])
            except OSError:
                os.makedirs(app.config['TEMP_UPLOAD_FOLDER'])
            fn.save(filename)                      
            
            image, thumb = store_image(app.config, filename)
            
            return render_template('upload_file.html', 
                                    data={'thumb': thumb, 'img': image})
        else:
            flash("You either didn't supply a file or it wasn't a valid image")
            return render_template('upload_file.html')
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