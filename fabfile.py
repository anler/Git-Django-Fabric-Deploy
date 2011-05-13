import os
from fabric.api import env, run, prompt, local, get
from fabric.utils import puts
from fabric import colors
from fabric.state import output

env.hosts = []
env.user = ''

dependencies = ['django==1.3']

releases_dir = '/tmp'
remote_releases_dir = '/tmp'

remote_staging_path = ''
remote_production_path = ''

project_folder = os.path.basename(os.path.dirname(__file__))


def staging():
    """
    Upload the archived project to the staging servers
    """
    project_name = _get_project_name()
    put('%s/%s.tar' % (releases_dir, project_name), 
        '%s/%s.tar' % (remote_releases_dir, project_name))
    run('cd %s && tar xzf %s %s' % (remote_releases_dir, project_name, remote_staging_path))


def production():
    """
    Upload the archived project to the production servers
    """
    project_name = _get_project_name()
    put('%s/%s.tar' % (releases_dir, project_name), 
        '%s/%s.tar' % (remote_releases_dir, project_name))
    run('cd %s && tar xzf %s %s' % (remote_releases_dir, project_name, remote_production_path))


def deploy():
    """
    Run tests
    Archive the project for uploading
    """
    project_name = _get_project_name()
    puts(project_name)
    local('python manage.py test --noinput --failfast')
    local('git archive --format=tar --prefix=radarhotelwww -o /tmp/radarhotelwww.tar HEAD')
    puts('Project stored at %s' % colors.red('%s/%s.tar' % (releases_dir, project_name), bold=True))


def _get_project_name():
    """
    Returns the a unique name composed in this form:
        
        `{project_name}_{git_commit_id}`
    """
    commit_id = local('git rev-parse HEAD', capture=True)
    return '%s_%s' % (project_folder, commit_id)
