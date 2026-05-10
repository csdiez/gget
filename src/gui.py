import logging

import PySimpleGUI as sg

import directory as d
from config import load_config, save_config
from main import cmd_pull, cmd_push
from repository import ping, remote_saves


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

    while 1:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, "Cancel"]:
            break

        if event == "Enter":
            game_title = values[0]
            dir = values[1]

            if game_title and dir:
                game = (game_title, dir)
                break

        if event:
            print(f"{event=}")

        if values:
            print(f"{values=}")

    window.close()

    return game


def remove_game() -> str:
    config = load_config()
    games = {game.replace("_", " "): game for game in config.keys()}

    layout: list = [
        [sg.Text("Choose a game to remove:")],
        [[sg.Button(game)] for game in games.keys()],
        [sg.Push(), sg.Button("Cancel"), sg.Push()],
    ]

    window = sg.Window("Remove Game", layout)

    game: str = ""

    while 1:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, "Cancel"):
            break

        if event:
            game = games[event]
            config.pop(games[event])
            save_config(config)
            break

    window.close()

    return game


def load_game(game_name: str) -> None:
    try:
        cmd_pull(game_name)
    except SystemError as se:
        git_cmd = se.args[0]
        err_code = se.args[1]
        stderr = se.args[2]

        warning(
            f"Couldn't load saves for {game_name}\nCommand: {git_cmd}\nError Code {err_code}: {stderr}"
        )


def main():
    config = load_config()

    restart = False

    online = True or not bool(ping(15))

    saved = remote_saves()

    dir_rows = [
        [
            sg.Text(game.replace("_", " ") + ":"),
            sg.Push(),
            sg.InputText(dir),
            sg.Button(
                "↧",
                tooltip="Download" if game in saved else "No available save",
                disabled=game not in saved,
            ),
            sg.Button("↥", tooltip="Upload"),
        ]
        for game, dir in config.items()
    ]

    dir_keys = list(config.keys())

    layout = [
        [
            sg.Button("+", tooltip="Add new directory"),
            sg.Button("-", tooltip="Remove a directory"),
            sg.Push(),
            sg.Text(
                "🟢" if online else "🔴", tooltip="Online" if online else "Offline"
            ),
            sg.Button("↧", tooltip="Download"),
            sg.Button("↥", tooltip="Upload"),
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
                config[dir_keys[i]] = dir
            save_config(config)

        if event == "+":
            game = add_game()
            if not game:
                warning("Empty input")
                continue

            game_name, dir = game

            if game_name in config:
                warning(f"{game_name} already exists")
                continue

            if not d.exists(dir):
                warning(f"Directory does not exist\n{dir}")
                continue

            config[game_name] = dir
            save_config(config)

            info(f"Added {game_name}")

            restart = True
            break

        if event == "-":
            game = remove_game()

            info(f"Removed {game}")

            restart = True
            break

        if event == "↧":
            if not confirmation("This will overwrite your local save data, continue?"):
                continue

            for game in config.keys():
                load_game(game)

            restart = True
            break

        elif event == "↥":
            diffs: dict[str, bool] = {}
            for game in config.keys():
                diffs[game] = cmd_push(game)

            if diffs:
                info(f"Uploaded save data for:\n{'\n'.join(diffs.keys())}")
                restart = True
                break

            else:
                info("No changes to upload.")

        elif isinstance(event, str):
            if "↧" in event:
                game = dir_keys[int(event[1]) // 2]

                if not confirmation(
                    f"This will overwrite your local save data, continue?\n{game}"
                ):
                    continue

                load_game(game)

                info(f"Loaded saves for {game}.")

                restart = True
                break

            elif "↥" in event:
                game = dir_keys[(int(event[1]) - 1) // 2]
                changed = cmd_push(game)

                if changed:
                    info(f"Uploaded saves for {game}.")

                    restart = True
                    break

                else:
                    info("No changes to upload.")

        # if event:
        #     print(f"{event=}")

        # if values:
        #     print(f"{values=}")

        pass

    window.close()

    if restart:
        main()


if __name__ == "__main__":
    main()
