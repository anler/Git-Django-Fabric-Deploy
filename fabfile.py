import os
from fabric.api import env, run, prompt, local, put, cd
from fabric.utils import puts
from fabric import colors
from fabric.state import output
from fabric.contrib.files import exists

env.hosts = []
env.user = ''

dependencies = []

releases_dir = os.path.join(os.path.dirname(__file__), 'releases')

remote_staging_path = ''
remote_production_path = ''

staging_virtualenv = ''
production_virtualenv = ''

project_folder = os.path.basename(os.path.dirname(__file__))


def staging():
    """
    Upload the archived project to the staging servers
    """
    project_name = _get_project_name()
    put('%s/%s.tar' % (releases_dir, project_name), 
        '%s/%s.tar' % (remote_staging_path, project_name))
    
    with cd(path):
        run('mkdir -p %(rel)s && cd %(rel)s && tar xf ../%(rel)s.tar && rm -f ../%(rel)s.tar' % {'rel': project_name})
        if exists('./release'):
            run('rm -rf release')
        # Point to the new release
        run('ln -sf %(path)s/%(rel)s %(path)s/release' % {'path': remote_staging_path, 'rel': project_name})
        collectstatic('%s/%s' % (remote_staging_path, project_name), staging_virtualenv, 'staging')
        syncdb('%s/%s' % (path, project_name), staging_virtualenv, 'staging')


def production():
    """
    Upload the archived project to the production servers
    """
    project_name = _get_project_name()
    put('%s/%s.tar' % (releases_dir, project_name), 
        '%s/%s.tar' % (remote_production_path, project_name))

    with cd(path):
        run('mkdir -p %(rel)s && cd %(rel)s && tar xf ../%(rel)s.tar && rm -f ../%(rel)s.tar' % {'rel': project_name})
        if exists('./release'):
            run('rm -rf release')
        # Point to the new release
        run('ln -sf %(path)s/%(rel)s %(path)s/release' % {'path': remote_production_path, 'rel': project_name})
        collectstatic('%s/%s' % (remote_production_path, project_name), production_virtualenv, 'production')
        syncdb('%s/%s' % (path, project_name), staging_virtualenv, 'production')


def deploy():
    """
    Run tests
    Archive the project for uploading
    """
    project_name = _get_project_name()
    puts(project_name)
    local('python manage.py test --noinput --failfast')
    local('git archive --format=tar -o %s/%s.tar HEAD' % (releases_dir, project_name))
    puts('Project stored at %s' % colors.red('%s/%s.tar' % (releases_dir, project_name), bold=True))


def rollback(steps=1):
    """
    Go backs `steps`times in the deployment history
    """
    project_name = _get_project_name('HEAD~%s' % steps)
    with cd(remote_staging_path):
        if exists(project_name):
            run('rm -rf release')
            # Point to the new release
            run('ln -sf %(path)s/%(rel)s %(path)s/release' % {'path': remote_staging_path, 'rel': project_name})
        else:
            puts(colors.red('The previous version `%s`does not exist' % project_name))


def collectstatic(app_path, virtualenv, appenv):
    """
    Django collectstatic command [see: http://docs.djangoproject.com/en/1.3/ref/contrib/staticfiles/#collectstatic]
    """
    with cd(app_path):
        run('export RADARHOTEL_ENV=%s && source %s/bin/activate && python manage.py collectstatic --noinput' % (appenv, virtualenv))


def syncdb(app_path, virtualenv, appenv):
    """
    Django syncdb command [see: http://docs.djangoproject.com/en/1.3/ref/django-admin/#syncdb]
    """
    with cd(app_path):
        run('export RADARHOTEL_ENV=%s && source %s/bin/activate && python manage.py syncdb --noinput' % (appenv, virtualenv))


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


def _send_to_servers():
    """
    Uploads the archived project to the servers
    """
    project_name = _get_project_name()
    put('%s/%s.tar' % (releases_dir, project_name), 
        '%s/%s.tar' % (remote_staging_path, project_name))
    
    return project_name, remote_staging_path


