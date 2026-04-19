import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--config",
    type=str,
    help="Path to config"
)

parser.add_argument