"""
Perform local encryption on of certain files.  The generated en/decryption key
is not protected from outsiders other than being in the user's home directory...
"""
import errno
from pathlib import Path

import cryptography.fernet
from cryptography.fernet import Fernet

from qslgen import cryptoKeyFile
from qslgen import userDir


def load_crypto_key():
    """
    Load or create an en/decryption key.
    """
    try:
        with open(cryptoKeyFile, 'rb') as keyFile:
            cryptoKey = keyFile.read()
            keyFile.close()
    except OSError as e:
        if e.errno == errno.ENOENT:
            print(f'\nNeed to create a key to encrypt local storage of API keys.')
            try:
                Path.mkdir(userDir)
            except FileExistsError:
                pass
        newCryptoKey = Fernet.generate_key()
        try:
            with open(cryptoKeyFile, 'wb') as keyFile:
                keyFile.write(newCryptoKey)
                keyFile.close()
                input(f'\nKey created and saved in {userDir}.\nPress Enter to continue...')
        except PermissionError:
            print(f'\nERROR:  Permission was denied when writing key file.')
        cryptoKey = newCryptoKey
    return cryptoKey


def encrypt_data(message, cryptoKey):
    """
    Encrypt data and return them for writing to file.
    """
    f = Fernet(cryptoKey)
    encryptedMessage = f.encrypt(message.encode())
    return encryptedMessage


def decrypt_data(message, cryptoKey):
    """
    Decrypt the data and return them for use in memory.
    """
    f = Fernet(cryptoKey)
    try:
        decryptedMessage = f.decrypt(message).decode()
    except (cryptography.fernet.InvalidToken, cryptography.fernet.InvalidSignature):
        print(f'\nThe crypto key supplied could not decrypt the file.')
        decryptedMessage = False
    return decryptedMessage
