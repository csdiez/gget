from datetime import datetime
import subprocess

import directory as d
    
class Repository:
    url: str
    path: str
    
    def __init__(self, url: str, path: str = ''):
        path = path or 'save'
        
        self.url = url
        self.path = path
        
    @classmethod
    def clone(cls, url: str, path: str) -> None:
        d.rm_dir(path)
        print(f'git clone {url} {path}')
        subprocess.call(['git', 'clone', url, path])
        
    def call(self, *args) -> str:
        call = ['git', '-C', self.path]
        call.extend(args)
        print(' '.join(call))
        return str(subprocess.check_output(call))

    def init(self) -> None:
        self.call('init', '-b', 'main')

    def switch(self, branch: str) -> None:
        branches = self.call('branch', '-l')
        args = ['switch']
        if branch not in branches:
            args.append('-c')
        args.append(branch)
        self.call(*args)

    def save_branch(self, branch: str, path: str = '') -> None:
        self.switch(branch)
        if path:
            try: self.call('pull')
            except: pass
            d.copy_dir(path, self.path)
        self.call('add', '.')
        self.call('commit', datetime.now().strftime("%d/%m/%Y_%H:%M:%S"))
        self.call('push')
        
    def load_branch(self, branch: str, path: str = '') -> None:
        self.switch(branch)
        self.call('pull')
        if path:
            d.copy_dir(self.path, path)