import os
from pathlib import Path
import shutil

def make_full_dir(path_name: str) -> Path:
    path = Path(path_name)
    path.mkdir(parents=True, exist_ok=True)
    for sub_dir in path.iterdir():
        pass
    return path

def copy_dir(src: str, dst: str):
    make_full_dir(src)
    make_full_dir(dst)
    shutil.copytree(src, dst, symlinks=True, dirs_exist_ok=True)
    
def rm_dir(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path)