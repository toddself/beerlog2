# B(eer)Log
B(eer)Log is a beer recipe generation system.  It allows you to model your 
equipment set, water profile, mash information, recipe data, etc. At also allows
"forking" recipes and keeping the historical data about each recipe as part of the
new recipe allowing ease of recipe modification and experimentation.  It also
will manage your ingredients inventory for you.  It will not, however, brew
the beer for you.

It also is a blogging engine that allows you to write a beer-recipe blog with
linking to the recipes for ease of people following your instruction.

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