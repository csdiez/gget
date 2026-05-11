import json
from pathlib import Path

CLOUD_DIR = Path.home() / ".gget"
REPO  = CLOUD_DIR / "saves.git"
CONFIG_FILE = CLOUD_DIR / "games.json"

def load_games() -> dict[str, str]:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except:
        return {}
    
def save_games(games: dict[str, str]) -> None:
    with open(CONFIG_FILE, 'w') as f:
        json.dump(games, f)