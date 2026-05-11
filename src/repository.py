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

def git(*args: str | Path, timeout: int = 0, **kwargs) -> tuple[str, int]:
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
        output = byte_f(te.stderr) + f"\nTimed out after {te.timeout} seconds.", 504
    else:
        output = result.stdout, result.returncode

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

    # def __enter__(self) -> Self:
    #     assert REPO.exists(), FileNotFoundError(f"{REPO} does not exist.")

    #     path = Path(self.path).parent
    #     self._original_dir = os.getcwd()

    #     repo_dir: Path = path / self.name
        
    #     shutil.rmtree(repo_dir, ignore_errors=True)
    #     git('clone', REPO, str(repo_dir))
    #     os.chdir(repo_dir)

    #     response = git('switch', self.name)

    #     if response[1]:
    #         git('switch', '-c', self.name)
    #         git('add', '.')
    #         git('commit', '-m', f'"Initialize {self.name}"')
    #         git('push', 'origin', 'HEAD')

    #     self._is_open = True
    #     return self

    # def __exit__(self, exc_type = None, exc = None, tb = None):
    #     shutil.rmtree(os.getcwd(), ignore_errors=True)

    #     os.chdir(REPO)
    #     git('switch', self.name)
    #     git('push', "--set-upstream", "origin", self.name)

    #     os.chdir(self._original_dir)
    #     self._is_open = False

    # def open(self) -> Self:
    #     return self.__enter__()
    
    # def close(self) -> None:
    #     return self.__exit__()

    # @staticmethod
    # def check_open(func):
    #     def wrapper(self: "Repository", *args, **kwargs):
    #         assert self._is_open, "Repository directory must be opened first."
    #         return func(self, *args, **kwargs)
    #     return wrapper


    def switch(self, branch: str = '') -> int:
        result = git('switch', branch or self.name)[1]
        if result:
            result = git('switch', '-c', self.name)[1]
            git('add', '.')
            git('commit', '-m', f'"Initialize {self.name}"')
            git('push', 'origin', 'HEAD')
        return result

    @cd(REPO)
    def save(self) -> None:
        cur_branch = git('status')[0].splitlines()[0].lstrip("On branch ").strip()
        self.switch()

        repo_path = REPO / Path(self.path).name
        shutil.rmtree(repo_path, ignore_errors=True)
        shutil.move(self.path, repo_path)

        git('add', '.')
        git('commit', '-m', f'"{socket.gethostname()}, {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}"')
        git('push')

        shutil.move(repo_path, self.path)

        self.switch(cur_branch)
        git('branch', '-f', '-D', self.name)

    @cd(REPO)
    def load(self) -> None:
        cur_branch = git('status')[0].splitlines()[0].lstrip("On branch ").strip()
        self.switch()
        path = REPO / Path(self.path).name
        if path.exists():
            shutil.rmtree(self.path, ignore_errors=True)
            shutil.move(path, self.path)
        self.switch(cur_branch)

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
    ping()