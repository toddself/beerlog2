from fabric.api import *

env.user = 'todd'
env.hosts = ['tron.robotholocaust.com']

def pack():
    local('python setup.py sdist --formats=gztar', capture=False)

def deploy():
    dist = local('python setup.py --fullname', capture=True).strip()
    put('dist/%s.tar.gz' % dist, '/tmp/beerlog.tar.gz')
    run('mkdir /tmp/beerlog')
    with cd('/tmp/beerlog'):
        run('tar xzf /tmp/beerlog.tar,gz')
        run('/usr/bin/env python setup.py install')
    