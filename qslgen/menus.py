import json
import re

import qsl_generator
from qrz_api.key_mgmt import load_api_keys, edit_api_keys
from qslgen import settingsFile
from qslgen import oauth


def main_menu(settings):
    opt = ''
    totalGeneratedQSLs = 0
    valid = False
    while not valid:
        opt = input(f'\nWelcome to QSLGen.\n\n'
                    f'Please select from the following options:\n'
                    f'[G]: Generate QSLs now.\n'
                    f'[S]: Change QSLGen settings.\n'
                    f'[Q]: Quit.\n'
                    f'\nType your selection and press enter: ').lower()
        match opt:
            case 'q':
                return opt, totalGeneratedQSLs
            case 's':
                settings = settings_menu(settings)
            case 'g':
                apiKeys = load_api_keys()
                if len(apiKeys) > 0:
                    totalGeneratedQSLs = qsl_generator.generator_main(settings, apiKeys)
                    valid = True
                else:
                    continue
            case _:
                print('\nInvalid input.')
    return opt, totalGeneratedQSLs


def settings_menu(settings):
    valid = False
    while not valid:
        opt = input(f'\n\nPlease select from the following options to update settings:\n'
                    f'[1]: Add, edit, or delete your QRZ Logbook API keys.\n'
                    f'\n'
                    f'[2]: Add your OAuth JSON data to be encrypted and stored locally.\n'
                    f'\n'
                    f'[3]: Change the date from which to fetch QSOs (this uses the API "MODSINCE" option).\n'
                    f'       Current:  {settings['dateSince']}\n'
                    f'[4]: Send emails or save emails locally for manual sending later.\n'
                    f'       Current:  {settings['email']}\n'
                    f'[5]: Keep or delete QSL cards saved on local drive.\n'
                    f'       Current:  {settings['keepQSLCard']}\n'
                    f'[6]: Change QSL Card image dimensions (should match the CALLSIGN_bg.jpg dimensions).\n'
                    f'       Current:  {settings['imgkitOptions']['crop-w']}x{settings['imgkitOptions']['crop-h']}\n'                    
                    f'[7]: Set/Change your name for the QSL emails.\n'
                    f'       Current:  {settings['myName']}\n'
                    f'[8]: Set/change your email address. (Only Gmail supported - see README to setup OAuth)\n'
                    f'       Current:  {settings['myEmail']}\n'
                    f'[9]: Do you want QSLGen to update QRZ QSOs with "eQSL Sent"?\n'
                    f'       Current:  {settings['updateQRZ']}\n'
                    f'[D]: Done, return to main menu.\n'
                    f'\nType your selection and press enter: ').lower()
        try:
            optNum = int(opt)
            match optNum:
                case 1:
                    apiKeys = load_api_keys()
                    edit_api_keys(apiKeys)
                case 2:
                    oauth_str = input(f'\nPlease copy and paste the ENTIRE contents of the JSON file you downloaded'
                                      f'when setting up your Google OAuth settings:  ')
                    oauth.write_oauth_data(oauth_str)
                case 3:
                    needDate = True
                    while needDate:
                        dateSince = input(f'\nPlease provide your desired date in the YYYY-MM-DD format:  ')
                        if re.match('^(\\d){4}-(\\d){2}-(\\d){2}', dateSince):
                            settings['dateSince'] = dateSince
                            needDate = False
                        else:
                            print('Invalid format.')
                case 4:
                    if settings['email'] == 'SEND':
                        settings['email'] = 'SAVE'
                    else:
                        settings['email'] = 'SEND'
                case 5:
                    if settings['keepQSLCard'] == 'SAVE':
                        settings['keepQSLCard'] = 'DELETE'
                    else:
                        settings['keepQSLCard'] = 'SAVE'
                case 6:
                    settings['imgkitOptions']['crop-w'] = input(f'\nPlease provide your desired image width:  ')
                    settings['imgkitOptions']['crop-h'] = input(f'\nPlease provide your desired image height:  ')
                case 7:
                    settings['myName'] = input(f'\nPlease enter your name as you '
                                               f'would like it to appear in the QSL emails:  ')
                case 8:
                    settings['myEmail'] = input(f'\nOnly Gmail supported since OAuth is the new defacto '
                                                f'security standard and Outlook does not have a public API. '
                                                f'\nRefer to the README to set your account up for OAuth.'
                                                f'\nPlease enter your email address:  ')
                case 9:
                    if settings['updateQRZ'] == 'YES':
                        settings['updateQRZ'] = 'NO'
                    else:
                        settings['updateQRZ'] = 'YES'
                case _:
                    print('\nInvalid input.')

        except ValueError:
            if opt == 'd':
                try:
                    with open(settingsFile, 'w') as sf:
                        json.dump(settings, sf)
                        sf.close()
                except Exception as e:
                    print(f'There was an error writing the settings file:'
                          f'{e}')
                return settings
            else:
                print('\nInvalid input.')
