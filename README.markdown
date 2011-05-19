This is a solution I use to easily deploy my django apps.

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
