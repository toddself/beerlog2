import hashlib
from functools import wraps

from flask import request, flash, redirect, render_template, url_for, session
from sqlobject import AND

from settings import PASSWORD_SALT
from blog.models import Users

def login():
    error = None
    if request.method == 'POST':
        pclear = request.form['password']
        pcrypt = hashlib.sha256("%s%s" % (PASSWORD_SALT, pclear)).hexdigest()
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
            return redirect(url_for('list_entries'))

    return render_template('login.html', error=error)

def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('list_entries'))
    
def require_auth(callback):
    @wraps(callback)
    def auth(*args, **kwargs):
        if session.get('logged_in'):
            return callback(*args, **kwargs)
        else:
            flash("You must be authenticated to access this section")
            return redirect(url_for('list_entries'))
    return auth