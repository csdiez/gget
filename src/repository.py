import subprocess

def clone(url:str, *args) -> None:
    call = ['git', 'clone', url, 'save']
    call.extend(args)
    subprocess.call(call)
    
clone("https://github.com/csdiez/gget.git", '-b', 'test')