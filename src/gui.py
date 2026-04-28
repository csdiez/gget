import PySimpleGUI as sg

from config import Config
import directory as d
from repository import Repository

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
        [sg.Push(), sg.Text(prompt), sg.Push],
        [sg.Button('Confirm'), sg.Button('Cancel')]
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
        [sg.Text(text)],
        [sg.Button('Close')]
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

def main(config: Config = Config()):
    restart = False

    repo = Repository(config.repo_link, config.save_dir)
    online = repo.ping()
    
    dir_rows = [
        [
            sg.Text(game.replace('_', ' ') + ':'), sg.Push(), sg.Text(dir), sg.Push(),
            sg.Button('↧', tooltip="Download"), sg.Button('↥', tooltip="Upload")
        ] for game, dir in config.dirs.items()
    ]

    dir_keys = list(config.dirs.keys())
    
    layout = [
        [
            sg.Button('+', tooltip="Add new directory."), sg.Button('-', tooltip="Remove a directory."), sg.Push(),
            sg.Text('🟢' if online else '🔴', tooltip='Online' if online else 'Offline'),
            sg.Button('↧', tooltip="Download"), sg.Button('↥', tooltip="Upload")
        ],
        dir_rows,
        [sg.Push(), sg.Button("Refresh", tooltip="Reopen this window."), sg.Button('Close',), sg.Push()]
    ]

    window = sg.Window("Gget", layout)

    while 1:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, 'Close']:
            break

        if event == 'Refresh':
            restart = True
            break

        if event == '+':
            game = add_game()
            if not game:
                warning("Empty input")
                continue

            game_name, dir = game

            if game_name in config.dirs:
                warning(f"{game_name} already exists")
                continue
            
            if not d.exists(dir):
                warning(f"Directory does not exist\n{dir}")
                continue

            # local_save
            # d.make_full_dir()
            # d.copy_dir(dir, )

            pass

        if event == '-':
            pass

        if event == '↧':
            if not confirmation('This will overwrite your local save data, continue?'):
                continue
            
            for game, dir in config.dirs.items():
                repo.load()
                d.copy_dir(d.join(config.save_dir, game), dir)

        elif event == '↥':
            for game, dir in config.dirs.items():
                d.copy_dir(dir, d.join(config.save_dir, game))
                repo.save()

        elif isinstance(event, str):
            if '↧' in event:
                game = dir_keys[int(event[1]) // 2]
                dir = config.dirs[game]
                
                if not confirmation(f'This will overwrite your local save data, continue?\n{game}'):
                    continue
                
                repo.load()
                d.copy_dir(d.join(config.save_dir, game), dir)

            elif '↥' in event:
                game = dir_keys[(int(event[1]) - 1) // 2]
                dir = config.dirs[game]
                d.copy_dir(dir, d.join(config.save_dir, game))
                repo.save()

        if event:
            print(f"{event=}")

        if values:
            print(f"{values=}")

        pass
    
    window.close()

    if restart:
        main(config)

if __name__ == "__main__":
    main()