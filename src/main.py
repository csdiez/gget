from args import args
from config import Config

if __name__ == "__main__":
    config = Config(args.config)
    
    if args.add:
        config.add_dir(*args.add)
    
    if args.remove:
        config.del_dir(args.remove)
        
    if args.list:
        print(config.dirs)
        
    if args.source:
        print(config.repo)
    
    if args.set_source:
        config.set_repo(args.set_source)
    
    pass