import json
import hashlib
import os
from datetime import datetime
from decimal import Decimal

from flask import Flask
from sqlobject import connectionForURI, sqlhub
from sqlobject.dberrors import OperationalError

from beerlog.helpers import format_time, sqlobject_to_dict, LazyView
from beerlog.blog.models import Tag, Entry
from beerlog.image.models import Image
from beerlog.admin.models import Users, Role#, Permission
from beerlog.admin.views import require_auth
from beerlog.comment.models import Comment
from beerlog.brewery.models import Hop, Grain, Extract, HoppedExtract, Yeast,\
                                   Water, Misc, Mineral, Fining, Flavor,\
                                   Spice, Herb, BJCPStyle, BJCPCategory,\
                                   MashTun, BoilKettle, EquipmentSet,\
                                   MashProfile, MashStep, MashStepOrder,\
                                   Recipe, RecipeIngredient, Inventory
from beerlog.brewery.importers import process_bjcp_styles, process_bt_database

app = Flask(__name__)
app.config.from_object('beerlog.settings')

if app.config['DEBUG']:
    prefix = 'DEBUG'
else:
    prefix = 'LIVE'
    
try:
    app.static_url_path = app.config['%s_STATIC_URL_PATH' % prefix]
except KeyError:
    pass

try:
    app.static_folder = app.config['%s_STATIC_FOLDER' % prefix]
except KeyError:
    pass

app.jinja_env.filters['dateformat'] = format_time

def url(url_rule, import_name, **options):
    view = LazyView('beerlog.'+import_name)
    app.add_url_rule(url_rule, view_func=view, **options)

# ADMIN VIEWS
url('/login', 'admin.views.login', methods=['GET', 'POST'])
url('/logout', 'admin.views.logout')
url('/admin/users/edit/<user_id>/password/', 'admin.views.change_password')
url('/admin/users/', 'admin.views.list_users')
url('/admin/users/edit/<user_id>/', 'admin.views.edit_user', methods=['POST', 'GET'])
url('/admin/users/create/', 'admin.views.create_user', methods=['POST', 'GET'])
url('/admin/users/edit/<user_id>/delete/', 'admin.views.delete_user')


# BLOG VIEWS
url('/', 'blog.views.list_entries')
url('/entry/<entry_id>/', 'blog.views.list_entries')
url('/entry/<year>/', 'blog.views.list_entries')
url('/entry/<year>/<month>/', 'blog.views.list_entries')
url('/entry/<year>/<month>/<day>/', 'blog.views.list_entries')
url('/entry/<year>/<month>/<day>/<slug>/', 'blog.views.list_entries')
url('/entry/archives/json/', 'blog.views.list_archives')
url('/entry/edit/', 'blog.views.edit_entry', methods=['POST', 'GET'])
url('/entry/edit/<entry_id>/', 'blog.views.edit_entry', methods=['POST', 'GET'])
url('/entry/edit/<entry_id>/delete/', 'blog.views.delete_entry')

# COMMENT VIEWS
url('/entry/<entry_id>/comment/add/', 'comment.views.add_comment')

# IMAGE VIEWS
url('/image/', 'image.views.list_images')
url('/image/add/', 'image.views.create_image', methods=['GET','POST'])
url('/image/<image_id>/delete/', 'image.views.delete_image')

# BREWERY VIEWS
## BJCP
url('/brewery/bjcp/', 'brewery.bjcp.views.list_styles')
url('/brewery/bjcp/style/<style_id>/json/', 'brewery.bjcp.views.get_style_json')
## RECIPE
url('/brewery/', 'brewery.recipe.views.list_recipes')
url('/brewery/recipe/', 'brewery.recipe.views.list_recipes')
url('/brewery/recipe/<recipe_id>/batch/', 'brewery.recipe.views.list_recipes')
url('/brewery/recipe/edit/', 'brewery.recipe.views.edit_recipe', methods=['POST', 'GET'])
url('/brewery/recipe/<recipe_id>/', 'brewery.recipe.views.edit_recipe', methods=['POST', 'GET'])
url('/brewery/recipe/batch/<recipe_id>/', 'brewery.recipe.views.edit_recipe', methods=['POST', 'GET'])
## INGREIDENTS
url('/brewery/ingredients/<ingredient>/json/', 'brewery.ingredients.views.list_ingredients')
## MODELS
url('/brewery/models/<model>/json/', 'brewery.recipe.views.pymodel_as_json')

@app.before_request
def before_request():
    connect_db(app.config)

@app.teardown_request
def teardown_request(exception):
    pass

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
    tables = [Entry, Users, Tag, Image, Hop, Grain, Extract, HoppedExtract,
              Yeast, Water, Misc, Mineral, Fining, Flavor, Spice, Herb,
              BJCPStyle, BJCPCategory,  MashTun, BoilKettle, EquipmentSet,
              MashProfile, MashStep, MashStepOrder, Recipe, RecipeIngredient,
              Inventory, Comment, Role]#, Permission]
    for table in tables:
        try:
            table.createTable()
        except OperationalError:
            pass
    

    adef = config['ADMIN_USERNAME']
    admin = Users(email=adef, first_name=adef, last_name=adef, alias=adef)
    admin.set_pass(config['PASSWORD_SALT'], config['ADMIN_PASSWORD'])
    admin.admin = True
    # uncomment when you're sorted out your little permissions thingy
    # for role in config['SYSTEM_ROLES']:
    #     r = Role(name=role)
    # admin.addRole(config['SYSTEM_ROLES'].index(config['ADMIN']))


    process_bjcp_styles()
    process_bt_database()

if __name__ == '__main__':
    app.run()