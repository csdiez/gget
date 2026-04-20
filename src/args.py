import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--config",
    type=str,
    help="Path to config"
)

parser.add_argument(
    "-a", "--add",
    nargs=2,
    type=str,
    help='Add new path with "name", "path" pairing.'
)

parser.add_argument(
    "-r", "--remove",
    type=str,
    help="Remove path by name."
)

parser.add_argument(
    "-l", "--list",
    action="store_true",
    help="List all paths."
)

parser.add_argument(
    "-s", "--source",
    action="store_true",
    help="Get the git repository URL."
)

parser.add_argument(
    "-S", "--set-source",
    type=str,
    help="Set the git repository URL."
)

args = parser.parse_args()