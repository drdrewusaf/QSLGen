"""
QSLGen Main
"""
import json
import re

import menus as menu
from logger import writer as log_writer
from qslgen import settingsFile
from qslgen import today


def load_settings():
    """
    Load the settings json file.
    :return settings: dict of settings from the settings json file
    """
    with open(settingsFile, 'r') as sf:
        settings = json.load(sf)
        sf.close()
    if not re.match('^(\\d){4}-(\\d){2}-(\\d){2}', settings['dateSince']):
        settings['dateSince'] = today
    return settings


def main():
    """
    Main function
    """
    settings = load_settings()
    opt, totalGeneratedQSLs = menu.main_menu(settings)
    if opt == 'q':
        exit(0)
    else:
        print(f'\nQSLGen finished sending and updating {totalGeneratedQSLs} '
              f'QSLs for confirmed QSOs since {settings['dateSince']} '
              f'using the provided API keys.\n')
        if totalGeneratedQSLs > 0:
            print(f'You should check your email sent items and QRZ.com to ensure everything processed as expected.\n\n')
        input(f'Press Enter to exit.')
    # End the log entries
    log_writer('', end=True)
    exit(0)


if __name__ == "__main__":
    main()
