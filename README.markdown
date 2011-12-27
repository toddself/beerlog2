# B(eer)Log
B(eer)Log is a beer recipe generation system.  It allows you to model your 
equipment set, water profile, mash information, recipe data, etc. At also allows
"forking" recipes and keeping the historical data about each recipe as part of the
new recipe allowing ease of recipe modification and experimentation.  It also
will manage your ingredients inventory for you.  It will not, however, brew
the beer for you.

It also is a blogging engine that allows you to write a beer-recipe blog with
linking to the recipes for ease of people following your instruction.

# Requirements
Python 2.6 or higher
Flask 
Flask-WTF
SQLObject
Fabric (for remote deployment only)
WTForms
Boto (for S3 image storage)
PIL (for image resizing) (libjpeg is required if you're going to use jpg images)
Python-Dateutil 1.5

setup.py will install these packages (and their dependancies) for you.

Much like the Flask project I highly recommend the use of a virtualenv 
(`console.sh` requires one to be installed as `env/`)

# Settings
If you wish to use the image uploading functionality, you'll need to either 
change the upload code (`beerlog/images/views.py`) to handle a different storage
back-end, or you'll need to supply some AWS S3 credentials.

# Running
## Testing
`python runserver.py`

## Production
1. Webserver that supports WSGI
2. `python setup.py install`
3. Point your webserver to `/var/www_apps/deploy.wsgi`

Beerlog is &copy; 2011 Todd Kennedy <todd.kennedy@gmail.com> and released under
the MIT license