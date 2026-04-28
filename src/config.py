import json
import os

class Config:
    path: str
    repo_link: str
    save_dir: str
    dirs: dict[str, str]

    def __init__(self, path: str = ''):
        path = path or os.path.join(__file__.rstrip('/src/config.py'), 'config', 'config.json')
        assert os.path.isfile(path), f"{path} is not a valid config file."

        self.path = path
        
        with open(path) as f:
            config = json.load(f)
        
        for key, t, default in [('repo_link', str, ""),
                                ('save_dir', str, "save"),
                                ('dirs', dict, {})]:
            setattr(self, key, config.get(key, default))

    def set_repo(self, url: str) -> None:
        self.repo_link = url
        self.save()
        
    def set_save_dir(self, path: str) -> None:
        self.save_dir = path
        self.save()
        
    def add_dir(self, name: str, path: str) -> None:
        self.dirs[name] = path
        self.dirs = dict(sorted(self.dirs.items(), key=lambda x: x[0]))
        self.save()
        
    def del_dir(self, name: str) -> None:
        self.dirs.pop(name)
        self.save()
        
    def save(self) -> None:
        with open(self.path, 'w') as f:
            json.dump({'repo': self.repo_link, 'save_dir': self.save_dir, 'dirs': self.dirs}, f, indent=4)