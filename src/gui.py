import logging
import os

import PySimpleGUI as sg

from repository import Repository, ping
from config import load_games, save_games

def confirmation(prompt: str) -> bool:
    decision = False

    layout = [
        [sg.Push(), sg.Text(prompt), sg.Push()],
        [sg.Push(), sg.Button("Confirm"), sg.Button("Cancel"), sg.Push()],
    ]

    window = sg.Window("", layout)

    while 1:
        event, _ = window.read()

        if event in [sg.WIN_CLOSED, "Cancel"]:
            break

        if event == "Confirm":
            decision = True
            break

    window.close()

    return decision


def text_and_close(title: str, text: str) -> None:
    layout = [
        [sg.Push(), sg.Text(text), sg.Push()],
        [sg.Push(), sg.Button("Close", focus=True), sg.Push()],
    ]
    print(text)
    window = sg.Window(title, layout)

    while 1:
        event, _ = window.read()

        if event:
            break

    window.close()


def info(text: str) -> None:
    logging.info(text)
    text_and_close("Info", text)


def warning(text: str) -> None:
    logging.warning(text)
    text_and_close("Warning", text)


def error(text: str) -> None:
    logging.info(text)
    text_and_close("Error", text)


def add_game() -> tuple[str, str] | None:
    layout = [
        [sg.Text("Game Title"), sg.Push(), sg.InputText()],
        [sg.Text("Game Directory"), sg.Push(), sg.InputText()],
        [sg.Button("Enter"), sg.Button("Cancel")],
    ]

    window = sg.Window("Add Game", layout)

    game: tuple[str, str] | None = None

    while not game:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, "Cancel"]:
            break

        if event == "Enter":
            game_title = values[0]
            dir = values[1]

            if game_title and dir:
                game = (game_title, dir)

        if event:
            print(f"{event=}")

        if values:
            print(f"{values=}")

    window.close()

    return game


def remove_game(*all_games: str) -> str:
    games = {game.replace("_", " "): game for game in all_games}

    layout: list = [
        [sg.Text("Choose a game to remove:")],
        [[sg.Button(game)] for game in games.keys()],
        [sg.Push(), sg.Button("Cancel"), sg.Push()],
    ]

    window = sg.Window("Remove Game", layout)

    game: str = ""

    while not game:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, "Cancel"):
            break

        if event:
            game = games[event]

    window.close()

    return game

def main():
    games = load_games()

    restart = False

    online = not bool(ping())

    dir_rows = [
        [
            sg.Text(game.replace("_", " ") + ":"),
            sg.Push(),
            sg.InputText(dir),
            sg.Button("↧", tooltip="Download", disabled=not online),
            sg.Button("↥", tooltip="Upload", disabled=not online),
        ]
        for game, dir in games.items()
    ]

    game_names = list(games.keys())

    layout = [
        [
            sg.Button("+", tooltip="Add new directory"),
            sg.Button("-", tooltip="Remove a directory"),
            sg.Push(),
            sg.Text("🟢" if online else "🔴", tooltip="Online" if online else "Offline"),
            sg.Button("↧", tooltip="Download", disabled=not online),
            sg.Button("↥", tooltip="Upload", disabled=not online),
        ],
        dir_rows,
        [
            sg.Push(),
            sg.Button("Save", tooltip="Save current directories"),
            sg.Button("Refresh", tooltip="Reopen this window"),
            sg.Button("Close", tooltip="Close Window"),
            sg.Push(),
        ],
    ]

    window = sg.Window("Gget", layout)

    while 1:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, "Close"]:
            break

        if event == "Refresh":
            restart = True
            break

        if event == "Save" and isinstance(values, dict):
            for i, dir in values.items():
                games[game_names[i]] = dir
            save_games(games)

        if event == "+":
            game = add_game()
            if not game:
                warning("Empty input")
                continue

            game_name, dir = game

            if game_name in games:
                warning(f"{game_name} already exists")
                continue

            if not os.path.exists(dir):
                warning(f"Directory does not exist\n{dir}")
                continue

            games[game_name] = dir
            save_games(games)

            info(f"Added {game_name}")

            restart = True
            break

        if event == "-":
            game = remove_game(*games.keys())

            games.pop(game)
            save_games(games)

            info(f"Removed {game}")

            restart = True
            break

        if event == "↧":
            if not confirmation("This will overwrite your local save data, continue?"):
                continue

            for game in game_names:
                Repository(game, games[game]).load()

            info("Loaded saves for all games")

        elif event == "↥":
            diffs: list[str] = []
            for game in games.items():
                if Repository(*game).save():
                    diffs.append(game[0])

            if diffs:
                info(f"Uploaded save data for:\n{'\n'.join(diffs)}")
            else:
                info("No changes to upload.")

        elif isinstance(event, str):
            if "↧" in event:
                game = game_names[int(event[1]) // 2]

                if not confirmation(f"This will overwrite your local save data, continue?\n{game}"):
                    continue

                Repository(game, games[game]).load()

                info(f"Loaded saves for {game}.")

            elif "↥" in event:
                game = game_names[(int(event[1]) - 1) // 2]
                if Repository(game, games[game]).save():
                    info(f"Uploaded save data for {game}")
                else:
                    info("No changes to upload")

        if event:
            print(f"{event=}")

        if values:
            print(f"{values=}")

        pass

    window.close()

    if restart:
        main()


if __name__ == "__main__":
    main()
