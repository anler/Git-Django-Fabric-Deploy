This is a solution I use to easily deploy my django apps.

Usage:

    fab deploy staging

or

    fab deploy production


Development box:
---------------

The tree structure that must have the django project:
    
    myproject/
        releases/
            myproject<git-commit-id>.tar
        ...
        config/
            development.py
            staging.py
            production.py

The original myproject/settings.py must be replaced by:
    
    import os

    try:
        environ = os.environ['MYPROJECT_ENV']
    except KeyError:
        environ = 'development'

        configs = {
            'development': 'development',
            'staging': 'staging',
            'production': 'production',
        }

        config_module = __import__('config.%s' % configs[environ], globals(), locals(), 'myproject')
        for setting in dir(config_module):
            if setting == setting.upper():
                locals()[setting] = getattr(config_module, setting)


Deployment (Production) box:
---------------------------

The structure of the project in the server:
    
    my_app/
        staging/
            myproject<git-commit-id>
            release     - Symbolic link to a concrete release: myproject<git-commit-id>
        production/
            ...         - Same as above

