import platform
from os.path import join as fjoin

# data directory for windows
if platform.system() == "Windows":
    data_dir = 'c:\\www\\'
    protocol = ':/'
else:
    data_dir = '/var/www_apps/'
    protocol = '://'

DEBUG = True
LIVE_STATIC_URL_PATH = YOUR_INFO_HERE
LIVE_STATIC_FOLDER = YOUR_INFO_HERE

# SECRETS
SECRET_KEY = YOUR_INFO_HERE
PASSWORD_SALT = YOUR_INFO_HERE

# ADMIN
ADMIN_USERNAME = YOUR_INFO_HERE
ADMIN_PASSWORD = YOUR_INFO_HERE

# RECAPCHA FOR COMMENTS
RECAPTCHA_USE_SSL = True
RECAPTCHA_PUBLIC_KEY = YOUR_INFO_HERE
RECAPTCHA_PRIVATE_KEY = YOUR_INFO_HERE
RECAPTCHA_OPTIONS = YOUR_INFO_HERE (if needed)

# DB
DB_DRIVER = 'sqlite'
DB_NAME = fjoin(data_dir, 'beerlog.db')
DB_PROTOCOL = protocol

# AWS
AWS_ACCESS_KEY = YOUR_INFO_HERE
AWS_SECRET_KEY = YOUR_INFO_HERE
AWS_BUCKET_NAME = YOUR_INFO_HERE

# IMAGES
IMAGE_FULL_SIZE = 800.0
TEMP_UPLOAD_FOLDER = '/tmp/beerlog/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])
IMAGE_BASEPATH = YOUR_INFO_HERE

# MISC
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


