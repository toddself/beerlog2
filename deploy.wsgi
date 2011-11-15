import os, sys
os.environ['BEERLOG_SETTINGS'] = '/var/www_apps/beerlog/settings.cfg'
sys.path.append('/var/www_apps/beerlog')
from beerlog import app