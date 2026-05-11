
from datetime import datetime
import os
from pathlib import Path
import shutil

from args import args
from repository import Repository, get_branches, git, ping
from config import REPO, load_games, save_games
from directory import CD

def cmd_init(repo_url: str) -> None:
    """Initialise the bare repo and attach a remote."""
    if os.path.exists(REPO):
        shutil.rmtree(REPO)
    
    git("clone", repo_url, str(REPO))

def cmd_add(game_name: str, save_path: str) -> None:
    """Register a game's save directory (no files moved)."""
    path = Path(save_path).expanduser().resolve()

    assert path.exists(), f"Save path does not exist: {path}"

    cfg = load_games()
    cfg[game_name] = str(path)
    save_games(cfg)

    _write_sparse_gitignore(path)

    print(f"Registered '{game_name}' → {path}")

def cmd_remove(game_name: str) -> None:
    config = load_games()

    assert game_name in config, f"{game_name} not found."

    config.pop(game_name)
    save_games(config)

def cmd_push(game_name: str) -> bool:
    """Stage, commit, and push a game's saves."""
    cfg = load_games()
    
    assert game_name in cfg, f"Unknown game '{game_name}'. Run: add <game> <path>"

    save_path = Path(cfg[game_name])

    work_tree = save_path.parent
    rel_folder = save_path.name

    git_games("add", rel_folder, work_tree=work_tree)

    # Check if there's actually anything to commit
    status = git_games_output("status", "--porcelain", rel_folder, work_tree=work_tree)
    if not status:
        print(f"'{game_name}' — nothing to push, saves are up to date.")
        return False

    git_games("commit", "-m", f"sync: {game_name}, {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}", work_tree=work_tree)
    git_games("push", "origin", "HEAD:main", work_tree=work_tree)

    print(f"Pushed '{game_name}' saves to remote.")

    return True

def cmd_pull(game_name: str) -> None:
    """Pull latest saves for a game from remote."""
    cfg = load_games()
    
    assert game_name in cfg, f"Unknown game '{game_name}'. Run: add <game> <path>"
    
    save_path = Path(cfg[game_name])
    work_tree = save_path.parent

    git_games("fetch", "origin")
    git_games("checkout", "origin/main", "--", game_name, work_tree=work_tree)

    print(f"Pulled latest saves for '{game_name}' into {save_path}")

def cmd_list() -> None:
    """List all registered games."""
    cfg = load_games()
    if not cfg:
        print("No games registered yet.")
        return

    print(f"{'Game':<25} Save Path")
    print("-" * 60)
    for name, path in sorted(cfg.items()):
        exists = "✓" if Path(path).exists() else "✗ (missing)"
        print(f"{name:<25} {path}  {exists}")


# --- Internal ----------------------------------------------------------------

def _write_sparse_gitignore(save_path: Path) -> None:
    """
    Place a .gitignore in the work-tree root (save_path.parent) that tracks
    only the registered game folders, preventing accidental staging of
    unrelated files sitting in the same parent directory.
    """
    cfg = load_games()
    work_tree = save_path.parent
    gitignore = work_tree / ".gitignore"

    tracked = {Path(p).name for p in cfg.values() if Path(p).parent == work_tree}

    # Ignore everything, then un-ignore each tracked folder
    lines = ["# managed by gget", "*", ""]
    for folder in sorted(tracked):
        lines.append(f"!{folder}/")

    gitignore.write_text("\n".join(lines) + "\n")

if __name__ == "__main__":

    if args.add:
        cmd_add(*args.add)
    
    if args.remove:
        cmd_remove(args.remove)
        
    if args.games:
        cmd_list()

    if args.ping:
        print(ping())

    if args.init:
        cmd_init(args.init)

    if REPO.exists():
        with CD(REPO):
            git('pull', '--all', cwd=REPO)
            branches = get_branches()
            games = load_games()
            for branch in branches:
                if branch not in games:
                    git('switch', branch)
                    break
            else:
                git('switch', '-c', 'main')
    
    if args.save_all or 1:
        for game in load_games().items():
            Repository(*game).save()
       
    if args.load_all:
        for game in load_games().items():
            Repository(*game).load()
    
    pass