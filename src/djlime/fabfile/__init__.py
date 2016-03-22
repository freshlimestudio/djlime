# -*- coding: utf-8 -*-
# fabfile for Django:
import time
import re
import os
import sys
from contextlib import contextmanager as _contextmanager

from fabric.api import *
from fabric.colors import *
from fabric.state import commands
from fabric.contrib.files import comment, uncomment


if sys.platform.startswith('linux'):
    env.remote_deployment = True
else:
    env.remote_deployment = False

__all__ = (
    'deploy_to_dev_server', 'dev', 'setup', 'deploy', 'venv',
    'deploy_version', 'rollback', 'releases', 'update_code',
    'update_code_from_repo', 'update_code_from_archive',
    'install_requirements', 'symlink_current_release', 'collect_static_files',
    'syncdb', 'migrate', 'cleanup', 'debug', 'restart_webserver', 'clean',
    'setup_local', 'setup_remote',
)

# globals
env.git_host = ''
env.project_name = ''
env.venv_name = ''
env.repo = 'git@{git_host}:/projects/{project_name}'.format(**env)
env.use_ssh_config = env.remote_deployment
env.shared_dirs = 'config media static releases/{current,previous}'
env.requirements_file = 'requirements.txt'


@task(default=True)
def deploy_to_dev_server():
    execute(dev)
    execute(deploy)


def _set_venv_name():
    if not env.venv_name:
        env.venv_name = env.project_name


@task
def dev():
    """Development server"""
    env.user = ''
    env.branch = ''
    env.hosts = []
    env.vhosts_root = "/var/www/vhosts"
    env.host_name = ''
    env.django_settings_module = '{project_name}.settings'.format(**env)
    env.vhost_path = '{vhosts_root}/{project_name}.{host_name}'.format(**env)
    env.release_path = "{vhost_path}/releases/current".format(**env)


@task(alias='up')
def setup():
    """Initial deployment setup"""
    _set_venv_name()
    run("mkvirtualenv {venv_name}".format(**env))
    with cd(env.vhost_path):
        run('mkdir -p {shared_dirs}'.format(**env))
    execute(setup_remote)


@task(alias='dep')
def deploy(param=''):
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and
    then restart the webserver
    """
    require('branch', 'vhosts_root', 'host_name', 'vhost_path', 'release_path',
            provided_by=['dev', 'prod'])
    _set_venv_name()
    try:
        print(green("Start deployment to production"))
        env.release = time.strftime('%Y%m%d%H%M%S')
        execute('update_code')
        execute('symlink_current_release')
        execute('install_requirements')
        execute('collect_static_files')
        execute('cleanup')
        if param == 'migrate':
            execute('migrate')
        if 'after_deploy' in commands:
            execute('after_deploy')
        execute('restart_webserver')
    except (SystemExit, KeyboardInterrupt):
        tarball = '{release}.tar.gz'.format(**env)
        if os.path.exists(tarball):
            print('Cleanup tarball')
            os.remove(tarball)


@task
def after_deploy():
    pass


@_contextmanager
def venv():
    _set_venv_name()
    require('django_settings_module', provided_by=['dev', 'prod'])
    with cd(env.release_path):
        with shell_env(DJANGO_SETTINGS_MODULE=env.django_settings_module):
            with prefix('workon {venv_name}'.format(**env)):
                yield


@task
def deploy_version(version):
    """Specify a specific version to be made live"""
    require('hosts', provided_by=['prod', 'dev'])
    env.version = version
    with cd(env.vhost_path):
        run("rm -rf releases/previous; mv -f releases/current releases/previous;")
        run("ln -s {version} releases/current".format(**env))
        run("ln -nfs {vhost_path}/config/local_settings.py {release_path}/{project_name}/local_settings.py".format(**env))
    restart_webserver()


@task
def rollback():
    """
    Limited rollback capability. Simply loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    print(green("Rollback deployed changes"))
    require('hosts', provided_by=['prod', 'dev'])
    with cd(env.vhost_path):
        run("mv -f releases/current releases/_previous;")
        run("mv -f releases/previous releases/current;")
        run("mv -f releases/_previous releases/previous;")
    restart_webserver()


def releases():
    """List a releases made"""
    with cd(env.vhost_path):
        env.releases = sorted(run('ls -x releases').split())
        if len(env.releases) >= 1:
            env.current_revision = env.releases[-1]
            env.current_release = "releases/{current_revision}".format(**env)
        if len(env.releases) > 1:
            env.previous_revision = env.releases[-2]
            env.previous_release = "releases/previous"


@task
def update_code():
    """Create an archive from the current Git master branch and upload it"""
    if env.remote_deployment:
        update_code_from_repo()
    else:
        update_code_from_archive()


@task
def update_code_from_repo():
    require('release', provided_by=['deploy'])
    print(green("Update code from git"))
    result = local('git ls-remote {repo} {branch}'.format(**env), capture=True)
    revdata = re.split(r'[\t\n]', result)
    env.rev = revdata[0]
    raw_commands = (
        "if [ -d {vhost_path}/cached-copy ]; then cd {vhost_path}/cached-copy",
        "git fetch -q origin",
        "git reset -q --hard {rev}",
        "git clean -q -d -x -f; else git clone -q {repo} {vhost_path}/cached-copy",
        "cd {vhost_path}/cached-copy",
        "git checkout -q -b deploy {rev}; fi"
        )
    run(' && '.join(map(lambda c: c.format(**env), raw_commands)))
    run('cp -RPp {vhost_path}/cached-copy {vhost_path}/releases/{release}'.format(**env))


@task
def update_code_from_archive():
    """Pack local repository copy to archive and upload to server"""
    require('release', provided_by=['deploy'])
    print(green("Create local git snapshot"))
    result = local('git ls-remote {repo} {branch}'.format(**env), capture=True)
    revdata = re.split(r'[\t\n]', result)
    env.rev = revdata[0]

    result = local('git rev-parse --revs-only {rev}'.format(**env), capture=True)
    local_revdata = re.split(r'[\t\n]', result)
    if local_revdata:
        if local_revdata[0] == env.rev:
            local('git archive --format=tar.gz {branch} -o {release}.tar.gz'.format(**env))
            run("mkdir -p {vhost_path}/releases/{release}".format(**env))
            put('{release}.tar.gz'.format(**env), '/tmp/')
            run("cd {vhost_path}/releases/{release} && tar zmxf /tmp/{release}.tar.gz".format(**env))
            run('rm -rf /tmp/{release}.tar.gz'.format(**env))
            os.remove('{release}.tar.gz'.format(**env))
        else:
            abort(red("Please update you repository from {repo} remote.".format(**env)))


@task
def install_requirements(param=''):
    """Install the required packages from the requirements file using pip"""
    with venv():
        print(green("Install runtime requirements"))
        if param == "upgrade":
            env.upgrade = "--upgrade"
        else:
            env.upgrade = ''
        run("pip install -r {requirements_file} {upgrade}".format(**env))


@task
def symlink_current_release():
    """Symlink our current release"""
    require('release', provided_by=['deploy'])
    with cd(env.vhost_path):
        run("rm -rf releases/previous; mv -f releases/current releases/previous;")
        run("ln -s {release} releases/current".format(**env))
        run("ln -nfs {vhost_path}/config/local_settings.py {release_path}/{project_name}/local_settings.py".format(**env))


@task
def collect_static_files():
    """Collect static files"""
    with venv():
        print(green("Collect static files"))
        run("django-admin.py collectstatic -v0 --noinput".format(**env))


@task
def syncdb(param=''):
    """Update the database"""
    with venv():
        print(green("Run syncdb for apps"))
        run('django-admin.py syncdb -v0'.format(**env))


@task
def migrate(param=''):
    """Update the database"""
    with venv():
        print(green("Migrate apps"))
        run("django-admin.py migrate".format(**env))


@task
def cleanup():
    """Clean up old releases"""
    with hide('running', 'stdout'):
        if 'releases' not in env:
            releases()
        size = len(env.releases)
        if len(env.releases) > 5:
            directories = env.releases
            directories.reverse()
            del directories[:5]
            dirs_count = len(directories)
            env.directories = ' '.join(["{0}/releases/{1}".format(env.vhost_path, release) for release in directories])
            run("rm -rf {directories}".format(**env))
            print(red("Cleaned {0} of {1} releases".format(dirs_count, size)))


@task
def debug(param="on"):
    """Toogle DEBUG variable in local_settings.py"""
    with cd(env.path):
        config_path = '{vhost_path}/config/local_settings.py'.format(**env)
        if param == "on":
            uncomment(config_path, r'(DEBUG)')
        else:
            comment(config_path, r'^(DEBUG)')
        execute(restart_webserver)


@task(alias='restart')
def restart_webserver():
    """Restart the web server"""
    with cd(env.path):
        if env.django_settings_module.split('.')[-1] == 'stage':
            run('touch {release_path}/{project_name}/wsgi_stage.py'.format(**env))
        else:
            run('touch {release_path}/{project_name}/wsgi.py'.format(**env))


@task
def clean():
    local('find . -name "*.pyc" -exec rm -f {} \;')


@task(alias='setup-local')
def setup_local():
    env.venvwrapper = local('which virtualenvwrapper.sh', capture=True)
    local('source {venvwrapper} && workon {venv_name} && add2virtualenv .'.format(**env), shell='/bin/bash')
    local('echo "export DJANGO_SETTINGS_MODULE={django_settings_module}" >> ~/.virtualenvs/{venv_name}/bin/postactivate'.format(**env))
    local('echo "unset DJANGO_SETTINGS_MODULE" >> ~/.virtualenvs/{venv_name}/bin/postdeactivate'.format(**env))


@task(alias='setup-remote')
def setup_remote():
    with venv():
        run('add2virtualenv {release_path}'.format(**env), shell='/bin/bash')
        run('echo "export DJANGO_SETTINGS_MODULE={django_settings_module}" >> ~/.virtualenvs/{venv_name}/bin/postactivate'.format(**env))
        run('echo "unset DJANGO_SETTINGS_MODULE" >> ~/.virtualenvs/{venv_name}/bin/postdeactivate'.format(**env))
