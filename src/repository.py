from multiprocessing import Manager, Process
from pathlib import Path

import subprocess

from directory import BARE_REPO

def git(*args: Path | str, timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
    cmd = ['git']
    cmd.extend([str(arg) for arg in args])
    
    m = Manager()
    response = m.dict()

    def check(d: dict[str, subprocess.CompletedProcess]) -> None:
        r = subprocess.run(cmd, **(kwargs or {"capture_output": True, "text": True}))
        d[' '.join(cmd)] = r

    p = Process(target=check, args=[response])

    try:
        p.start()
        p.join(timeout)
        assert not p.is_alive(), "Timed out."
    except Exception as e:
        p.terminate()
        p.join()
        raise e
    else:
        result = response.values()[0]
        return result

def git_output(*args: str, timeout: int = 30, **kwargs) -> str:
    """Same as git() but returns stdout as a stripped string."""
    return git(*args, timeout=timeout, **kwargs).stdout.strip()

def git_games(*args: str, timeout: int = 30, work_tree: Path | None = None, **kwargs) -> subprocess.CompletedProcess:
    arg_list = list(args)
    if work_tree:
        arg_list.append(f"--work-tree={work_tree}")
    return git(f"--git-dir={BARE_REPO}", *arg_list, timeout=timeout, **kwargs)

def git_games_output(*args, timeout: int = 30, work_tree: Path | None = None, **kwargs) -> str:
    arg_list = list(args)
    if work_tree:
        arg_list.append(f"--work-tree={work_tree}")
    return git_output(f"--git-dir={BARE_REPO}", *arg_list, timeout=timeout, work_tree=work_tree, **kwargs)

def ping() -> int:
    """
    Ping loaded repo from the home directory
    Sends the return code from the command (0=pass, else=fail)
    """
    return git_games('ls-remote').returncode