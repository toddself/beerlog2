import hashlib
from functools import wraps
from datetime import datetime

from flask import request, flash, redirect, render_template, url_for, session
from sqlobject import AND, OR, SQLObjectNotFound

from beerlog.admin.models import Users, generate_password, Role#, Permission
from beerlog.admin.forms import LoginForm, EditUserForm, CreateUserForm, ChangePasswordForm
from beerlog.image.models import Image
from beerlog.settings import PASSWORD_SALT

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
    @require_auth
    @wraps(callback)
    def admin(*args, **kwargs):
        try:
            user = Users.get(session.get('user_id'))
            if user.admin:
                return callback(*args, **kwargs)
            else:
                flash("Admins only")
                return redirect(url_for('list_entries'))
        except SQLObjectNotFound:
            flash("You're not even logged in")
            return redirect(url_for('list_entries'))
    return admin

def require_role(role_name, callback):
    @wraps(callback)
    def role(*args, **kwargs):
        error = False
        message = "Unauthorized access"
        uid = session.get('user_id')
        try:
            role = list(Role.select(Role.q.name==role_name))[0]
        except (SQLObjectNotFound, ValueError, IndexError):
            error = True
            message = "Role %s is not a valid role" % role_name
            
        try:
            user = Users.get(user_id)
        except SQLObjectNotFound:
            error = True
            message = "Sorry, you are not permitted to access this"
        
        if error:
            flash(message)
            return redirect(url_for('list_entries'))
        else:
            return callback(*args, **kwargs)
    return role
    
def require_permission(permission_type, obj, callback):
    @wraps(callback)
    def permission(*args, **kwargs):
        if has_permission(permission_type, obj):
            return callback(*args, **kwargs)
        else:
            flash("Sorry you cannot access or edit this object")
            return redirect(url_for('list_entries'))
    return permission

def has_permission(permission_type, obj, user_id):
    try:
        uid = Users.get(user_id)
    except SQLObjectNotFound:
        flash("You must be logged in to access this page")
        return redirect(url_for('login'))
    else:
        obj_type = obj.__class__.__name__
        perm = Permission.select(AND(permission.q.object_type==obj_type,
                                     permission.q.object_id==obj.id))
        if user in perm.user or [r for role in user.role if rol in perm.role]:
            return True
        else:
            return False

@require_auth
def change_password(user_id=0):
    pass_form = ChangePasswordForm()
    if pass_form.validate_on_submit():
        logged_in_as = session.get('user_id')
        if user_id != logged_in_as:
            flash("You can only change your own password!")
            return redirect(url_for('list_entries'))        
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

@require_auth
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

@require_admin
def create_user():
    user_form = CreateUserForm()
    if user_form.validate_on_submit():
        user = Users(first_name = user_form.first_name.data,
                     last_name = user_form.last_name.data,
                     email = user_form.email.data,
                     password = generate_password(user_form.password.data),
                     alias = user_form.alias.data)
        if user_form.avatar.data:
            i = Image(url=user_form.alias.data)
            user.avatar = i
        flash("%s %s has been created" % (user.first_name, user.last_name))
        return redirect(url_for('list_users'))
    else:
        user = {'first_name': '',
                'last_name': '',
                'email': '',
                'password': '',
                'avatar': ''}
        return render_template('edit_user.html', data={'form': user_form,
                                                       'user': user})

@require_auth
def edit_user(user_id=-1):
    user_form = EditUserForm()
    if user_form.validate_on_submit():
        user = Users.get(user_form.user_id.data)
        if user.id == session.get('user_id') or user.admin:
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
            flash("Sorry, you're not allowed to do that")
            return redirect(url_for('edit_user', user_id=user.id))

    else:
        try:
            user = Users.get(user_id)
        except SQLObjectNotFound:
            user = {'first_name': '',
                    'last_name': '',
                    'email': '',
                    'password': '',
                    'avatar': ''}
        finally:
            return render_template('edit_user.html', data={'form': user_form,
                                                           'user': user})
@require_admin
def delete_user(user_id):
    try:
        user = User.get(user_id)
    except SQLObjectNotFound:
        flash("No user found with that ID")
        return redirect(url_for('list_entries'))
    else:
        user.active = False
        flash("%s set to inactive" % user.alias)
        return redirect(url_for('list_users'))