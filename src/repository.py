from multiprocessing import Manager, Process

from pythonping import ping
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
        str_call = ' '.join(call)
        print()
        m = Manager()
        response = m.dict()
        def check(d: dict[str, str]) -> None:
            r = str(subprocess.check_output(call))
            d[str_call] = r
        
        p = Process(target=check, args=[response])
        try:
            p.start()
            p.join(10)
            assert not p.is_alive(), "Timed out."
        except Exception as e:
            p.terminate()
            p.join()
            print(e)
            return ''
        else:
            print(response[str_call])
            return response[str_call]

    def ping(self) -> bool:
        return bool(self.call('ls-remote'))

    def init(self) -> None:
        self.call('init')
        self.call('switch', '-c', 'main')

    def save(self) -> None:
        self.call('add', '.')
        
        if "nothing to commit, working tree clean" in self.call('status'):
            return
        
        self.call('commit', '-m', datetime.now().strftime("%d/%m/%Y_%H:%M:%S"))
        self.call('push')
        
    def load(self) -> None:
        self.call('pull')
