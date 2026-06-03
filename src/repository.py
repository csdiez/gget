from dataclasses import dataclass
from datetime import datetime
import logging
import os
from pathlib import Path
import shutil
import socket
import subprocess
from typing import Self

from config import REPO
from directory import cd

def byte_f(b: bytes | str | None) -> str:
    if isinstance(b, str):
        return b
    elif isinstance(b, bytes):
        return b.decode('utf-8')
    return ''

def git(*args: str | Path, timeout: int = 30, **kwargs) -> tuple[str, int]:
    """Run a git command and return stdout. Raises exception on failure."""
    result = None

    command = ["git"]
    for arg in args:
        command.append(str(arg))

    print(' '.join(command))

    output: tuple[str, int]

    if timeout:
        kwargs['timeout'] = timeout

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            **kwargs
        )
    except subprocess.CalledProcessError as cpe:
        output = byte_f(cpe.stdout) + byte_f(cpe.stderr), cpe.returncode
    except subprocess.TimeoutExpired as te:
        output = byte_f(te.stderr) + f"Timed out after {te.timeout} seconds.", 504
    else:
        output = f"{result.stdout}{result.stderr}", result.returncode

    if output[0]:
        print(output[0])
    return output


class Repository:
    name: str
    path: str

    _is_open: bool
    _original_dir: str

    def __init__(self, name: str, path: str | Path) -> None:
        self.name = name
        self.path = str(path)

    def switch(self, branch: str = '') -> int:
        result = git('switch', branch or self.name)[1]
        if result:
            result = git('switch', '-c', self.name)[1]
            git('add', '.')
            git('commit', '-m', f'"Initialize {self.name}"')
            git('push', 'origin', 'HEAD')
        return result

    @cd(REPO)
    def save(self) -> bool:
        cur_branch = git('status')[0].splitlines()[0].lstrip("On branch ").strip()
        self.switch()

        repo_path = REPO / Path(self.path).name
        shutil.rmtree(repo_path, ignore_errors=True)
        shutil.move(self.path, repo_path)

        git('add', '.')
        git('commit', '-m', f'"{socket.gethostname()}, {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}"')
        result = git('push')[0]

        shutil.move(repo_path, self.path)

        self.switch(cur_branch)
        git('branch', '-f', '-D', self.name)

        return 'up-to-date' not in result

    @cd(REPO)
    def load(self) -> bool:
        cur_branch = git('status')[0].splitlines()[0].lstrip("On branch ").strip()
        self.switch()
        path = REPO / Path(self.path).name
        if path.exists():
            shutil.rmtree(self.path, ignore_errors=True)
            shutil.move(path, self.path)
            return True
        
        self.switch(cur_branch)
        return False

@cd(REPO)
def get_branches() -> list[str]:
    raw_branches = git('branch')[0].splitlines()
    return list(map(lambda s: str.strip(s, '* '), raw_branches))

def ping(timeout: int = 5) -> int:
    """
    Ping loaded repo from the home directory
    Sends the return code from the command (0=pass, else=fail)
    """
    assert REPO.exists(), FileNotFoundError(f"{REPO} does not exist.")

    return git("ls-remote", timeout=timeout, cwd=REPO)[1]
    
if __name__ == "__main__":
    result = git("push")
    pass