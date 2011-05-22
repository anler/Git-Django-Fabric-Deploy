"""
Django project structure:
    
    myproject/
        releases/
            myproject<git-commit-id>.tar
        ...

Server app structure:
    
    my_app/
        staging/
            myproject<git-commit-id>
            release     - Symbolic link to a concrete release
        production/
            ...         - Same as above
"""
import os
from fabric.api import env, run, prompt, local, put, cd
from fabric.utils import puts
from fabric import colors
from fabric.state import output
from fabric.contrib.files import exists

env.name = 'MYPROJECT_ENV'
env.hosts = []
env.user = ''

dependencies = []

project_folder = os.path.basename(os.path.dirname(__file__))

# releases_dir is the directory where to puto all the 
# released versions
# path is the path in the server to the app (staging or production)
# virtualenv is the path in the server to the used virtualenv (staging or production)
SETTINGS = {
    'releases_dir': os.path.join(project_folder, 'releases'),
    'staging': {
        'path': '',
        'virtualenv': ''
    },
    'production': {
        'path': '',
        'virtualenv': ''
    }
}


def staging():
    """
    Upload the archived project to the staging servers
    """
    project_name = _get_project_name()
    origin = '%s/%s.tar' % (SETTINGS['releases_dir'], project_name)
    destination = '%s/%s.tar' % (SETTINGS['staging']['path'], project_name)
    put(origin, destination)

    with cd(SETTINGS['staging']['path']):
        run('mkdir -p %(rel)s && cd %(rel)s && tar xf ../%(rel)s.tar && rm -f ../%(rel)s.tar' % {'rel': project_name})
        if exists('./release'):
            run('rm -rf release')
        # Point to the new release
        run('ln -sf %(path)s/%(rel)s %(path)s/release' % {'path': SETTINGS['staging']['path'], 'rel': project_name})
        syncdb('staging')


def production():
    """
    Upload the archived project to the production servers
    """
    pass


def deploy():
    """
    Run tests
    Archive the project for uploading
    """
    project_name = _get_project_name()
    puts(project_name)
    local('python manage.py test --noinput --failfast')
    local('git-archive-all --format=tar -o %s/%s.tar HEAD' % (SETTINGS['releases_dir'], project_name))
    puts('Project stored at %s' % colors.red('%s/%s.tar' % (SETTINGS['releases_dir'], project_name), bold=True))


def rollback(appenv, steps=1):
    """
    Go backs `steps`times in the deployment history
    """
    project_name = _get_project_name('HEAD~%s' % steps)
    with cd(SETTINGS[appenv]['path']):
        if exists(project_name):
            run('rm -rf release')
            # Point to the new release
            run('ln -sf %(path)s/%(rel)s %(path)s/release' % {'path': SETTINGS[appenv]['path'], 'rel': project_name})
        else:
            puts(colors.red('The previous version `%s`does not exist' % project_name))


def syncdb(appenv):
    """
    Django syncdb command [see: http://docs.djangoproject.com/en/1.3/ref/django-admin/#syncdb]
    """
    with cd('%s/release' % SETTINGS[appenv]['path']):
        run('export %s=%s && source %s/bin/activate && python manage.py syncdb --noinput' % (env.name, appenv, SETTINGS[appenv]['virtualenv']))


def _get_project_name(revision='HEAD'):
    """
    Returns the a unique name composed in this form:
        
        `{project_name}_{git_commit_id}`
    """
    if revision:
        commit_id = local('git rev-parse %s' % (revision,), capture=True)
    else:
        commit_id = 'norev'
    return '%s_%s' % (project_folder, commit_id)

