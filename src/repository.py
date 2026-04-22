import subprocess

def clone(url:str, *args, **kwargs) -> None:
    call = ['git', 'clone', url, 'save']
    for k, v in kwargs.items():
        call.append(k)
        call.append(v)
        
    subprocess.call(call)
    
clone("https://github.com/csdiez/gget.git")