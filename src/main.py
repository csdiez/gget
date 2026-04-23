import os

from args import args
from config import Config
from repository import Repository

if __name__ == "__main__":    
    config = Config(args.set_config)

    if args.config:
        print(f"{config.path=}")

    if args.add:
        config.add_dir(*args.add)
    
    if args.remove:
        config.del_dir(args.remove)
        
    if args.games:
        print(f"{config.dirs=}")
        
    if args.url:
        print(f"{config.repo_link=}")
    
    if args.set_url:
        config.set_repo(args.set_url)
        Repository.clone(config.repo_link, config.save_dir)
        
    if args.path:
        print(f"{config.save_dir=}")
        
    if args.set_path:
        config.set_save_dir(args.set_path)
        Repository.clone(config.repo_link, config.save_dir)

    repo = Repository(config.repo_link, config.save_dir)
    
    if args.init:
        repo.init()
    
    if args.save:
        path = config.dirs.get(args.save)
        assert path, f"{args.save} not found."
        repo.save_branch(args.save, path)
        
    if args.load:
        path = config.dirs.get(args.load)
        assert path, f"{args.load} not found."
        repo.load_branch(args.load, path)
    
    if args.save_all or True:
        for game, path in config.dirs.items():
            repo.save_branch(game, path)
       
    if args.load_all:
        for game, path in config.dirs.items():
            repo.load_branch(game, path)
    
    pass