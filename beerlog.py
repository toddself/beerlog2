from __future__ import division
from __future__ import absolute_import
import hashlib
import os
from datetime import datetime

from flask import Flask

# TODO REFACTOR COMMON OUT OF EXISTANCE
from common import connect_db, init_db

from blog.views import get_entry, edit_entry, delete_entry
from blog.models import Users
# from images.views import get_image, add_image, delete_image

# TODO USER EDITOR
from admin.views import login, logout, require_auth

app = Flask(__name__)
app.config.from_pyfile('settings.py')

if app.config['DB_DRIVER'] == 'sqlite':
    app.config['DB_NAME'] = os.path.join(os.getcwd(), app.config['DB_NAME'])
    app.config['DB_PROTOCOL'] = '://'

@app.before_request
def before_request():
    connect_db(app.config)

@app.teardown_request
def teardown_request(exception):
    pass

# admin routing
app.add_url_rule('/login', view_func=login, methods=['POST', 'GET'])
app.add_url_rule('/logout', view_func=logout)

# unauthenticated blog views
app.add_url_rule('/', view_func=get_entry)
app.add_url_rule('/entry/<entry_id>/', view_func=get_entry)
app.add_url_rule('/entry/<year>/<month>/<day>/', view_func=get_entry)
app.add_url_rule('/entry/<year>/<month>/<day>/<slug>/', view_func=get_entry)

# authenticated blog views
app.add_url_rule('/entry/edit/',
                 view_func=require_auth(edit_entry),
                 methods=['POST', 'GET'])
app.add_url_rule('/entry/edit/<entry_id>/', 
                 view_func=require_auth(edit_entry),
                 methods=['POST', 'GET'])
app.add_url_rule('/entry/edit/<entry_id>/delete/',
                 view_func=require_auth(delete_entry))

if __name__ == '__main__':
    app.run()