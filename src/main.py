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
        config.set_repo(args.source)
    
    pass