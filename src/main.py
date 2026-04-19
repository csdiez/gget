import argparse

import config

# Create the argument parser
parser = argparse.ArgumentParser(description="Process some parameters.")

# Add a boolean flag
parser.add_argument(
    "-v", "--verbose", 
    action="store_true", 
    help="Enable verbose output"
)

# Add an optional argument with a value
parser.add_argument(
    "-n", "--name", 
    type=str, 
    default="World", 
    help="Name to greet"
)

# Parse the arguments
args = parser.parse_args()

# Access the flag values
if args.verbose:
    print(f"Verbose mode enabled for {args.name}")
else:
    print(f"Greeting for {args.name}")   

# if __name__ == "__main__":
#     print(config.load_conf())