"""
API Key management tools for local storage
"""
import re

import qslgen.crypto as crypto
from qslgen import apiKeysFile


def edit_api_keys(newKeys):
    """
    Main menu for editing the apikeys.txt file.
    """
    editsDone = False
    while not editsDone:
        count = 0
        print(f'\nAPI keys currently in file and memory:')
        if len(newKeys) >= 1:
            for k in newKeys:
                print('[' + str(count) + ']: ' + ' ' + k)
                count += 1
        opt = input(f'\nOptions:\n'
                    f'[0-n]: Delete key by id above.\n'
                    f'[A]: Add new key(s).\n'
                    f'[D]: Done. Return to previous menu.\n'
                    f'\nType your selection and press enter: ').lower()
        if opt.isnumeric():
            try:
                newKeys.pop(int(opt))
            except IndexError:
                print(f'\nInvalid key id.')
        elif opt == 'd':
            if len(newKeys) < 1:
                print(f'\nCannot continue without at least one API key.\n')
            else:
                write_key_file(newKeys)
                editsDone = True
        elif opt == 'a':
            addedApiKeys = add_api_keys()
            if len(addedApiKeys) > 0:
                for k in addedApiKeys:
                    newKeys.append(k)
                print(f'\nAdded {len(addedApiKeys)} keys.')
        else:
            print(f'\nInvalid input.')
    return newKeys


def add_api_keys():
    """
    Based on user input, create an array of API keys to be added to the apikeys.txt file.
    """
    addedKeys = []
    finished = False
    while not finished:
        newKey = input(f'\nEnter API keys, with or without dashes. If you have more than one, '
                       f'use commas with NO spaces to separate each key.'
                       f'\nType "done" to finish.'
                       f'\nAdd API key(s): ')
        if newKey == 'done':
            finished = True
        elif ',' in newKey:
            for k in newKey.split(','):
                if validate_api_key(k):
                    addedKeys.append(k)
                    print(f'\nKey {k} added successfully.')
        elif validate_api_key(newKey):
            addedKeys.append(newKey)
            print(f'\nKey {newKey} added successfully.')
        else:
            pass
    return addedKeys


def validate_api_key(key):
    """
    Validate the key format - only validates format, does not validate typos/incorrect keys.
    """
    if re.match('(\\d|[A-z]){4}(-?)(\\d|[A-z]){4}(-?)(\\d|[A-z]){4}(-?)(\\d|[A-z]){4}(-?)', key):
        return True
    else:
        print(f'\n"{key}" format is invalid.')
        return False


def write_key_file(newKeys):
    """
    Encrypt the keys and write the data to the apikeys.txt file.
    """
    cryptoKey = crypto.load_crypto_key()
    newKeysText = ''
    try:
        with open(apiKeysFile, 'wb') as f:
            count = 0
            for k in newKeys:
                if count == len(newKeys) - 1:
                    newKeysText = newKeysText + k
                else:
                    newKeysText = newKeysText + k + ','
                    count += 1
            encryptedFile = crypto.encrypt_data(newKeysText, cryptoKey)
            f.write(encryptedFile)
        f.close()
    except PermissionError:
        print(f'\nERROR:  Permission was denied when writing API keys file.')


def load_api_keys():
    """
    Decrypt and load any API keys in the apikeys.txt file into memory.
    """
    newKeys = []
    cryptoKey = crypto.load_crypto_key()
    try:
        with open(apiKeysFile, 'rb') as f:
            decryptedFile = crypto.decrypt_data(f.read(), cryptoKey)
            if len(decryptedFile) > 0 and decryptedFile != 'u':
                newKeys = decryptedFile.split(',')
                f.close()
            else:
                print(f'\nNo API keys found. Please use the settings menu to add API keys.')
                return newKeys
    except FileNotFoundError:
        print(f'\nNo apikeys.txt file found.  Please use the settings menu to add API keys.')
        return newKeys
    if len(newKeys) == 0:
        print(f'\nNo API keys found. Please use the settings menu to add API keys.')
        return newKeys
    return newKeys
