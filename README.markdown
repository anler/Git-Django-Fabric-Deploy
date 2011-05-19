This is a solution I use to easily deploy my django apps.

Usage:

    fab deploy staging

or

    fab deploy production


Django project structure:
    
    myproject/
        releases/
            myproject<git-commit-id>.tar
        ...


Server app structure:
    
    my_app/
        staging/
            myproject<git-commit-id>
            release     - Symbolic link to a concrete release: myproject<git-commit-id>
        production/
            ...         - Same as above
