import hashlib
import os
from datetime import datetime

from flask import Flask
from sqlobject import connectionForURI, sqlhub
from sqlobject.dberrors import OperationalError

from beerlog.blog.models import Tag, Entry
from beerlog.image.models import Image
from beerlog.admin.models import Users
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

from beerlog.admin.views import *
from beerlog.blog.views import *
from beerlog.image.views import *
from beerlog.brewery.bjcp.views import *

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
              Inventory, Comment]
    for table in tables:
        try:
            table.createTable()
        except OperationalError:
            pass
    adef = config['ADMIN_USERNAME']
    admin = Users(email=adef, first_name=adef, last_name=adef, alias=adef)
    admin.set_pass(config['PASSWORD_SALT'], config['ADMIN_PASSWORD'])
    admin.admin = True
    process_bjcp_styles()
    process_bt_database()

if __name__ == '__main__':
    app.run()