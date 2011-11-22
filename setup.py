from setuptools import setup, find_packages

setup(
    name='Beerlog',
    version='0.50',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask','PIL', 'WTForms', 
                      'Flask-WTF', 'Boto', 'SQLObject', 'Fabric', 
                      'python-dateutil', ],
                      
    )