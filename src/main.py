
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

if __name__ == "__main__":

    if args.add:
        games = load_games()
        games[args.add[0]] = args.add[1]
        save_games(games)
    
    if args.remove:
        games = load_games()
        games.pop(args.remove)
        save_games(games)
        
    if args.games:
        print('\n'.join(load_games().keys()))

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
    
    if args.save_all:
        for game in load_games().items():
            Repository(*game).save()
       
    if args.load_all:
        for game in load_games().items():
            Repository(*game).load()
    
    pass