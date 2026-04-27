import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--config",
    action="store_true",
    help="Path to config"
)

parser.add_argument(
    "-C", "--set-config",
    type=str,
    help="Set the path to config"
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
    "-g", "--games",
    action="store_true",
    help="List all games and paths."
)

parser.add_argument(
    "-u", "--url",
    action="store_true",
    help="Get the git repository URL."
)

parser.add_argument(
    "-U", "--set-url",
    type=str,
    help="Set the git repository URL."
)

parser.add_argument(
    "-p", "--path",
    action="store_true",
    help="Get the git repository path."
)

parser.add_argument(
    "-P", "--set-path",
    type=str,
    help="Set the git repository path."
)

parser.add_argument(
    "--ping",
    action="store_true",
    help="Ping repository"
)

parser.add_argument(
    "-i", "--init",
    action="store_true",
    help="Initialize path"
)

parser.add_argument(
    "-s", "--save",
    type=str,
    help='Save one game by name.'
)

parser.add_argument(
    "-l", "--load",
    type=str,
    help='Load one game by name.'
)

parser.add_argument(
    "-sa", "--save_all",
    action="store_true",
    help='Save all games.'
)

parser.add_argument(
    "-la", "--load_all",
    action="store_true",
    help='Load all games.'
)

args = parser.parse_args()