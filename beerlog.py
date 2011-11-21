from __future__ import division
from __future__ import absolute_import
import hashlib
import os
from datetime import datetime

from flask import Flask, request, session, redirect, url_for, \
    render_template, flash
from sqlobject import AND
from werkzeug import secure_filename

from blog.models import Entry, Users, Tag
from blog.forms import PostForm
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