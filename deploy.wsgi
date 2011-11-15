import os
os.environ['BEERLOG_SETTINGS'] = '/var/www_apps/beerlog/settings.cfg'
os.environ['PYTHONPATH'] += '/var/www_apps/beerlog'
from beerlog import app