from __future__ import division
from __future__ import absolute_import

import hashlib
import os
from datetime import datetime
from functools import wraps

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from sqlobject import connectionForURI, sqlhub, AND

from models import Entry, Users, Tag
from forms import PostForm

app = Flask(__name__)
app.config.from_envvar('BEERLOG_SETTINGS')

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
    connection = connectionForURI("%s:/%s" % (app.config['DB_DRIVER'], app.config['DB_NAME']))
    sqlhub.processConnection = connection
    return True

def init_db():
    if os.path.exists(app.config['DB_NAME']):
        os.unlink(app.config['DB_NAME'])

    connect_db()
    Entry.createTable()
    Users.createTable()
    Tag.createTable()
    admin = Users(email=app.config['ADMIN_USERNAME'])
    admin.set_pass(app.config['PASSWORD_SALT'], app.config['ADMIN_PASSWORD'])

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
        return render_template('add_entry.html', form=post)

@require_auth
@app.route('/admin')
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