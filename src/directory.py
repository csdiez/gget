# Source - https://stackoverflow.com/a/13197763
# Posted by Brian M. Hunt, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-10, License - CC BY-SA 3.0

import os
from pathlib import Path

class CD:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath: str | Path):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def cd(dir: str | Path):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cwd = os.getcwd()
            os.chdir(dir)
            result = func(*args, **kwargs)
            os.chdir(cwd)
            return result
        return wrapper
    return decorator