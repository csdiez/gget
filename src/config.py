import json
import os

class Config:
    path: str
    repo: str
    dirs: dict[str, str]

    def __init__(self, path: str = ''):
        path = path or os.path.join('config', 'config.json')
        assert os.path.isfile(path), f"{path} is not a valid config file."

        self.path = path
        
        with open(path) as f:
            config = json.load(f)
        
        assert 'repo' in config, f'Broken Config File: {path}\n"repo" not found'
        assert 'dirs' in config, f'Broken Config File: {path}\n"dirs" not found'
        
        self.repo = config['repo']
        assert isinstance(self.repo, str), f'"repo" is of invalid type {type(self.repo)}'
        self.dirs = config['dirs']
        assert isinstance(self.dirs, dict), f'"dirs" is of invalid type {type(self.dirs)}'
        
    def set_repo(self, url: str) -> None:
        self.repo = url
        self.save()
        
    def add_dir(self, name: str, path: str) -> None:
        self.dirs[name] = path
        self.save()
        
    def del_dir(self, name: str) -> None:
        self.dirs.pop(name)
        self.save()
        
    def save(self) -> None:
        with open(self.path, 'w') as f:
            json.dump({'repo': self.repo, 'dirs': self.dirs}, f, indent=4)