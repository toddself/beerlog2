from setuptools import setup, find_packages

setup(
    name='beerlog',
    version='0.57',
    long_description=__doc__,
    packages=['beerlog',
             'beerlog.blog',
             'beerlog.admin',
             'beerlog.image',
             'beerlog.brewery',
             'beerlog.brewery.bjcp',
             'beerlog.brewery.recipe',
             'beerlog.comment'],
    include_package_data=True,
    zip_safe=False,
    data_files=[('/var/www_apps/', ['beerlog.wsgi',
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
