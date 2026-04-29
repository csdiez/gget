import PySimpleGUI as sg

from config import load_config, save_config
import directory as d
from main import cmd_pull, cmd_push
from repository import ping

def example():
    # All the stuff inside your window.
    layout = [  [sg.Text("What's your name?")],
                [sg.InputText()],
                [sg.Button('Ok'), sg.Button('Cancel')] ]

    # Create the Window
    window = sg.Window('Hello Example', layout)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()

        # if user closes window or clicks cancel
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break

        print('Hello', values[0], '!')

    window.close()

def confirmation(prompt: str) -> bool:
    decision = False

    layout = [
        [sg.Push(), sg.Text(prompt), sg.Push()],
        [sg.Push(), sg.Button('Confirm'), sg.Button('Cancel'), sg.Push()]
    ]

    window = sg.Window('', layout)

    while 1:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, 'Cancel']:
            break

        if event == 'Confirm':
            decision = True
            break

    window.close()

    return decision

def warning(text: str) -> None:
    layout = [
        [sg.Push(), sg.Text(text), sg.Push()],
        [sg.Push(), sg.Button('Close'), sg.Push()]
    ]

    window = sg.Window("Warning", layout)

    while 1:
        event, _ = window.read()

        if event:
            break

    window.close()

def add_game() -> tuple[str, str] | None:
    layout = [
        [sg.Text("Game Title"), sg.Push(), sg.InputText()],
        [sg.Text("Game Directory"), sg.Push(), sg.InputText()],
        [sg.Button('Enter'), sg.Button('Cancel')]
    ]

    window = sg.Window("Add Game", layout)

    game: tuple[str, str] | None = None

    while 1:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, 'Cancel']:
            break

        if event == 'Enter':
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

def remove_game() -> None:
    config = load_config()
    games = {game.replace('_', ' '): game for game in config.keys()}

    layout: list = [
        [sg.Text("Choose a game to remove:")],
        [[sg.Button(game)] for game in games.keys()],
        [sg.Push(), sg.Button("Cancel"), sg.Push()]
    ]

    window = sg.Window("Remove Game", layout)

    while 1:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            break

        if event:
            config.pop(games[event])
            save_config(config)
            break

    window.close()

def load_game(game_name: str) -> None:
    try:
        cmd_pull(game_name)
    except SystemError as se:
        git_cmd = se.args[0]
        err_code = se.args[1]
        stderr = se.args[2]

        warning(f"Couldn't load saves for {game_name}\nCommand: {git_cmd}\nError Code {err_code}: {stderr}")

def main():
    config = load_config()

    restart = False

    online = not bool(ping())
    
    dir_rows = [
        [
            sg.Text(game.replace('_', ' ') + ':'), sg.Push(), sg.InputText(dir),
            sg.Button('↧', tooltip="Download"), sg.Button('↥', tooltip="Upload")
        ] for game, dir in config.items()
    ]

    dir_keys = list(config.keys())
    
    layout = [
        [
            sg.Button('+', tooltip="Add new directory."), sg.Button('-', tooltip="Remove a directory."), sg.Push(),
            sg.Text('🟢' if online else '🔴', tooltip='Online' if online else 'Offline'),
            sg.Button('↧', tooltip="Download"), sg.Button('↥', tooltip="Upload")
        ],
        dir_rows,
        [sg.Push(), sg.Button("Save", tooltip="Save current directories."), sg.Button("Refresh", tooltip="Reopen this window."), sg.Button('Close', tooltip="Close Window."), sg.Push()]
    ]

    window = sg.Window("Gget", layout)

    while 1:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, 'Close']:
            break

        if event == 'Refresh':
            restart = True
            break

        if event == 'Save' and isinstance(values, dict):
            for i, dir in values.items():
                config[dir_keys[i]] = dir
            save_config(config)

        if event == '+':
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

            restart = True
            break

        if event == '-':
            remove_game()

        if event == '↧':
            if not confirmation('This will overwrite your local save data, continue?'):
                continue
            
            for game in config.keys():
                load_game(game)


        elif event == '↥':
            for game in config.keys():
                cmd_push(game)

        elif isinstance(event, str):
            if '↧' in event:
                game = dir_keys[int(event[1]) // 2]
                
                if not confirmation(f'This will overwrite your local save data, continue?\n{game}'):
                    continue
                
                load_game(game)

            elif '↥' in event:
                game = dir_keys[(int(event[1]) - 1) // 2]
                cmd_push(game)

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