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
    help="List all paths."
)

parser.add_argument(
    "-s", "--source",
    type=str,
    help="Set the git repository URL to pull saves from."
)
args = parser.parse_args()