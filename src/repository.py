from datetime import datetime
import subprocess

class Repository:
    url: str
    path: str
    
    def __init__(self, url: str, path: str = ''):
        path = path or 'save'
        
        self.url = url
        self.path = path
        
    def clone(self) -> None:
        call = ['git', 'clone', self.url, self.path]
        print(' '.join(call))
        subprocess.call(call)
        
    def call(self, *args) -> str:
        call = ['git', '-C', self.path]
        call.extend(args)
        print(' '.join(call))
        return str(subprocess.check_output(call))

    def init(self) -> None:
        self.call('init')
        self.call('switch', '-c', 'main')

    # def switch(self, branch: str) -> None:
    #     branches = self.call('branch', '-l')
    #     args = ['switch']
    #     if branch not in branches:
    #         args.append('-c')
    #     args.append(branch)
    #     self.call(*args)

    def save(self) -> None:
        # self.switch(branch)
        # if path:
        #     try: self.call('pull')
        #     except: pass
        #     d.copy_dir(path, self.path)
        self.call('add', '.')
        self.call('commit', '-m', datetime.now().strftime("%d/%m/%Y_%H:%M:%S"))
        self.call('push')
        
    def load(self) -> None:
        self.call('pull')
