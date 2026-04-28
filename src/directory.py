import os
from pathlib import Path
import shutil

CLOUD_DIR = Path.home() / ".gget"
BARE_REPO  = CLOUD_DIR / "repo.git"
CONFIG_FILE = CLOUD_DIR / "games.json"

def make_full_dir(path_name: str) -> Path:
    path = Path(path_name)
    path.mkdir(parents=True, exist_ok=True)
    return path

def copy_dir(src: str, dst: str):
    make_full_dir(src)
    make_full_dir(dst)
    shutil.copytree(src, dst, symlinks=True, dirs_exist_ok=True)
    
def rm_dir(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path)

def exists(path: str) -> bool:
    return os.path.exists(path)

def join(*path: str) -> str:
    return os.path.join(*path)