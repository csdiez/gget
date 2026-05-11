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
        save_games()
        return {}
    
def save_games(games: dict[str, str] = {}) -> None:
    CONFIG_FILE.write_text(json.dumps(games))