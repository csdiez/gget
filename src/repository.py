from multiprocessing import Manager, Process
from pathlib import Path

import subprocess

from directory import BARE_REPO

def git(*args: Path | str, timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
    cmd_args = ['git']
    cmd_args.extend([str(arg) for arg in args])
    
    cmd_str = ' '.join(cmd_args)

    m = Manager()
    response = m.dict()

    def check(d: dict[str, subprocess.CompletedProcess]) -> None:
        r = subprocess.run(cmd_args, **(kwargs or {"capture_output": True, "text": True}))
        d[cmd_str] = r

    p = Process(target=check, args=[response])

    try:
        p.start()
        p.join(timeout)
        assert not p.is_alive(), "Timed out."
        result: subprocess.CompletedProcess = response.values()[0]
        if result.returncode:
            raise SystemError(cmd_str, result.returncode, result.stderr)
    except AssertionError as ae:
        p.terminate()
        p.join()
        raise ae
    else:
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