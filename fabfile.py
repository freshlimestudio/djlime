from fabric.api import *


@task
def release():
    local('python setup.py sdist upload')
    local('python setup.py sdist upload -r lime')
    local('python setup.py bdist_wheel upload')
    local('python setup.py bdist_wheel upload -r lime')
