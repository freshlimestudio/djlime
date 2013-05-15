from fabric.api import *


@task
def release():
    local('python setup.py sdist upload')
    local('python setup.py sdist upload -r lime')
