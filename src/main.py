import os

from args import args
from config import Config
import directory as d
from repository import Repository

if __name__ == "__main__":
    if args.set_config:
        assert d.exists(args.set_config), f"Directory not found: {args.set_config}"

    config = Config(args.set_config)


    if args.config:
        print(f"{config.path=}")

    if args.add:
        assert d.exists(args.add[1]), f"Directory not found: {args.add[1]}"
        config.add_dir(*args.add)
    
    if args.remove:
        config.del_dir(args.remove)
        
    if args.games:
        print(f"{config.dirs=}")
        
    if args.url:
        print(f"{config.repo_link=}")
    
    if args.set_url:
        config.set_repo(args.set_url)
        
    if args.path:
        print(f"{config.save_dir=}")
        
    if args.set_path:
        config.set_save_dir(args.set_path)

    repo = Repository(config.repo_link, config.save_dir)

    if args.ping:
        repo.ping()

    if args.init:
        d.rm_dir(config.save_dir)
        d.make_full_dir(config.save_dir)
        repo.clone()
        
    if args.save:
        path = config.dirs.get(args.save)
        assert path, f"{args.save} not found."
        d.copy_dir(path, d.join(config.save_dir, args.save))
        repo.save()
        
    if args.load:
        path = config.dirs.get(args.load)
        assert path, f"{args.load} not found."
        d.copy_dir(d.join(config.save_dir, args.load), path)
        repo.load()
    
    if args.save_all:
        for game, path in config.dirs.items():
            d.copy_dir(path, d.join(config.save_dir, game))
        repo.save()
       
    if args.load_all:
        repo.load()
        for game, path in config.dirs.items():
            d.copy_dir(d.join(config.save_dir, game), path)
    
    pass