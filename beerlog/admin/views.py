import hashlib
from functools import wraps
from datetime import datetime

from flask import request, flash, redirect, render_template, url_for, session
from sqlobject import AND, SQLObjectNotFound

from admin.models import Users, generate_password
from admin.forms import LoginForm, EditUserForm, CreateUserForm, ChangePasswordForm
from image.models import Image

def login():
    error = None
    login_form = LoginForm()
    if login_form.validate_on_submit():
        u_req = Users.get(login_form.user_id.data)
        u_req.last_login = datetime.now()
        session['logged_in'] = True
        session['user_id'] = u_req.id
        flash('You were logged in')
        return redirect(url_for('list_entries'))
    return render_template('login.html', data={"form": login_form,
                                               "error": error})

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

def require_admin(callback):
    @wraps(callback)
    def admin(*args, **kwards):
        error = False
        if session.get('logged_in'):
            uid = session.get('user_id')
            try:
                user = Users.get(user_id)
                if user.admin:
                    return callback(*args, **kwards)
                else:
                    error = True
            except SQLObjectNotFound:
                error = True
        else:
            error = True

        if error:
            flash("You must be an admin to access this function")
            return redirect(url_for('list_entries'))
    return admin

def change_password(user_id=0):
    pass_form = ChangePasswordForm()
    if pass_form.validate_on_submit():
        try:
            user = Users.get(user_id)
        except SQLObjectNotFound:
            flash("You must provide a user ID")
            return redirect(url_for('list_users'))
        else:
            user.password = generate_password(pass_form.password.data)
            flash("Password successfully changed")
            return redirect(url_for('edit_user', user_id=user.id))
    else:
        try:
            user = Users.get(user_id)
        except SQLNotFoundError:
            flash("You must provide a user ID")
            return redirect(url_for('list_users'))
        else:
            return render_template('change_password.html', 
                                   data={'form': pass_form,
                                         'user_id': user.id})

def list_users(user_id=0):
    if user_id:
        try:
            users = list(Users.get(user_id))
        except SQLObjectNotFound:
            flash("No user found by that ID")
            return render_template('list_users.html')
    else:
        users = list(Users.select())
    return render_template('list_users.html', data={'users': users})

def edit_user(user_id=-1):
    if user_id > 0:
        user_form = EditUserForm()
    else:
        user_form = CreateUserForm()
    if user_form.validate_on_submit():
        try:
            user = Users.get(user_form.user_id.data)
        except (SQLObjectNotFound, AttributeError):
            user = Users(first_name = user_form.first_name.data,
                         last_name = user_form.last_name.data,
                         email = user_form.email.data,
                         password = generate_password(user_form.password.data),
                         avatar = user_form.avatar.data)
            if user_form.alias.data:
                user.alias = user_form.alias.data
            flash("%s %s has been created" % (user.first_name, user.last_name))
        else:
            user.first_name = user_form.first_name.data
            user.last_name = user_form.last_name.data
            user.email = user_form.email.data
            user.alias = user_form.alias.data
            user.last_modified = datetime.now()
            try:
                avatar = list(Image.select(Image.q.url==user_form.avatar.data))[0]
            except (SQLObjectNotFound, IndexError):
                pass
            else:
                user.avatar = avatar
            flash("%s %s has been updated" % (user.first_name, user.last_name))
        return redirect(url_for('list_users'))
    else:
        try:
            user = Users.get(user_id)
        except SQLObjectNotFound:
            user = {'first_name': '',
                    'last_name': '',
                    'email': '',
                    'password': '',
                    'avatar': ''}
        return render_template('edit_user.html', data={'form': user_form,
                                                       'user': user})

def delete_user(user_id):
    pass