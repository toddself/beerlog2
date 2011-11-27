from __future__ import division
from __future__ import absolute_import
import hashlib
import os
from datetime import datetime

from flask import Flask
from sqlobject import connectionForURI, sqlhub
from werkzeug.utils import secure_filename

# blog stuff
from blog.views import list_entries, edit_entry, delete_entry
from blog.models import Users, Tag, Entry

# image stuff
from image.views import list_images, create_image
from image.models import Image

# TODO USER EDITOR
from admin.views import login, logout, require_auth

app = Flask(__name__)
app.config.from_pyfile('settings.py')

if app.config['DB_DRIVER'] == 'sqlite':
    app.config['DB_NAME'] = os.path.join(os.getcwd(), app.config['DB_NAME'])
    app.config['DB_PROTOCOL'] = '://'

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
    Image.createTable()
    admin = Users(email=config['ADMIN_USERNAME'])
    admin.set_pass(config['PASSWORD_SALT'], config['ADMIN_PASSWORD'])

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
app.add_url_rule('/', view_func=list_entries)
app.add_url_rule('/entry/<entry_id>/', view_func=list_entries)
app.add_url_rule('/entry/<year>/<month>/<day>/', view_func=list_entries)
app.add_url_rule('/entry/<year>/<month>/<day>/<slug>/', view_func=list_entries)

# authenticated blog views
app.add_url_rule('/entry/edit/',
                 view_func=require_auth(edit_entry),
                 methods=['POST', 'GET'])
app.add_url_rule('/entry/edit/<entry_id>/', 
                 view_func=require_auth(edit_entry),
                 methods=['POST', 'GET'])
app.add_url_rule('/entry/edit/<entry_id>/delete/',
                 view_func=require_auth(delete_entry))
app.add_url_rule('/image/', view_func=require_auth(list_images))
app.add_url_rule('/image/add/',
                view_func=require_auth(create_image), 
                methods=['POST'])

if __name__ == '__main__':
    app.run()