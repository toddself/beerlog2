import platform
from setuptools import setup, find_packages

# data directory for windows
if platform.system() == "Windows":
    data_dir = 'c:\\www\\'
else:
    data_dir = '/var/www_apps/'

setup(
    name='beerlog',
    version='0.57.911',
    long_description=__doc__,
    packages=['beerlog',
             'beerlog.blog',
             'beerlog.admin',
             'beerlog.image',
             'beerlog.brewery',
             'beerlog.brewery.bjcp',
             'beerlog.brewery.recipe',
             'beerlog.brewery.ingredients',
             'beerlog.comment'],
    include_package_data=True,
    zip_safe=False,
    data_files=[(data_dir, ['beerlog.wsgi',
                            'beer_data.xml',
                            'styleguide2008.xml'])],
    install_requires=['Flask',
                      'PIL',
                      'WTForms',
                      'Flask-WTF',
                      'Boto',
                      'SQLObject',
                      'Fabric',
                      'python-dateutil==1.5',], 
    )
