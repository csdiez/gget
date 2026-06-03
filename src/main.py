
from datetime import datetime
import os
from pathlib import Path
import shutil

from args import args
from repository import Repository, get_branches, git, ping
from config import REPO, Games, load_games, save_games
from directory import CD

if __name__ == "__main__":

    if args.add:
        with Games() as games:
            games[args.add[0]] = args.add[1]
    
    if args.remove:
        with Games() as games:
            games.pop(args.remove)
        
    if args.games:
        print('\n'.join(load_games().keys()))

    if args.ping:
        print(ping())

    if args.init:
        shutil.rmtree(REPO, ignore_errors=True)
        git("clone", args.init, str(REPO))

    if not REPO.exists():
        raise FileNotFoundError(r"Repository is not initialized.\nAdd the repository with the -i {url}")
    
    if args.save_all or args.load_all:
        if ping():
            raise ConnectionError("Cannot connect to git repo.")

        with CD(REPO):
            git('pull', '--all', timeout=5)
            branches = get_branches()
            games = load_games()
            for branch in branches:
                if branch not in games:
                    git('switch', branch)
                    break
            else:
                git('switch', '-c', 'main')
        
        if args.save_all:
            print("Saved:")
            for game in load_games().items():
                if Repository(*game).save():
                    print(game[0])
        
        if args.load_all:
            print("Loaded:")
            for game in load_games().items():
                Repository(*game).load()
                print(game[0])
        
    pass