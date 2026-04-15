from qrz_api.key_mgmt import load_api_keys


def main_menu():
    """
    This is the main menu for QSLGen.
    """
    global apiKeys
    opt = ''
    validInputs = ['g', 'u', 'q']
    valid = False
    while not valid:
        opt = input('\nWelcome to QSLGen.\n\n'
                    'Please select from the following options:\n'
                    '[G]: Generate QSLs now.\n'
                    '[U]: Update or create your apikey.txt file.\n'
                    '[Q]: Quit.\n'
                    '\nType your selection and press enter: ').lower()
        if opt in validInputs:
            if opt == 'q':
                return opt
            elif opt == 'u' or 'g':
                apiKeys, valid = load_api_keys(opt)
        else:
            print('\nInvalid input.')
    return opt, apiKeys