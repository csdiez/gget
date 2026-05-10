import logging
import subprocess
from multiprocessing import Manager, Process
from pathlib import Path
from typing import Any

from directory import BARE_REPO


def git(
    *args: Path | str, timeout: int = 30, **kwargs: Any
) -> subprocess.CompletedProcess:
    cmd_args = ["git"]
    cmd_args.extend([str(arg) for arg in args])

    cmd_str = " ".join(cmd_args)

    m = Manager()
    response = m.dict()

    def check(d: dict[str, subprocess.CompletedProcess]) -> None:
        r = subprocess.run(
            cmd_args, **(kwargs or {"capture_output": True, "text": True})
        )
        d[cmd_str] = r

    p = Process(target=check, args=[response])

    try:
        p.start()
        p.join(timeout)
        assert not p.is_alive(), "Timed out."
        result: subprocess.CompletedProcess = response.values()[0]
        if result.returncode:
            logging.error(cmd_str, result.returncode, result.stderr)
            raise SystemError(cmd_str, result.returncode, result.stderr)
    except subprocess.CalledProcessError as e:
        p.terminate()
        p.join()
        raise e
    else:
        logging.info(cmd_str, result.stdout)
        return result


def git_output(*args: str, timeout: int = 30, **kwargs: Any) -> str:
    """Same as git() but returns stdout as a stripped string."""
    return git(*args, timeout=timeout, **kwargs).stdout.strip()


def git_games(
    *args: str, timeout: int = 30, work_tree: Path | None = None, **kwargs: Any
) -> subprocess.CompletedProcess:
    if work_tree:
        return git(
            f"--work-tree={work_tree}",
            f"--git-dir={BARE_REPO}",
            *args,
            timeout=timeout,
            **kwargs,
        )
    else:
        return git(f"--git-dir={BARE_REPO}", *args, timeout=timeout, **kwargs)


def git_games_output(
    *args, timeout: int = 30, work_tree: Path | None = None, **kwargs: Any
) -> str:
    if work_tree:
        return git_output(
            f"--work-tree={work_tree}",
            f"--git-dir={BARE_REPO}",
            *args,
            timeout=timeout,
            **kwargs,
        )
    else:
        return git_output(f"--git-dir={BARE_REPO}", *args, timeout=timeout, **kwargs)


def ping(timeout: int = 30) -> int:
    """
    Ping loaded repo from the home directory
    Sends the return code from the command (0=pass, else=fail)
    """
    try:
        return git_games("ls-remote", timeout=timeout).returncode
    except subprocess.CalledProcessError as e:
        print(e, f"Timed out after {timeout} seconds")
        return 1


def remote_saves() -> list[str]:
    """Return all top-level directories in the remote repo."""
    result = git_games(
        "ls-tree", "-d", "--name-only", "origin/main", capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    return sorted(result.stdout.strip().splitlines())
