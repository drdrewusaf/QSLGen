"""
Perform local encryption on of the API keys.  The generated en/decryption key
is not protected from outsiders...
"""
from cryptography.fernet import Fernet


def load_crypto_key():
    """
    Load or create an en/decryption key.
    """
    try:
        with open('config\\key.key', 'rb') as keyFile:
            cryptoKey = keyFile.read()
            keyFile.close()
    except FileNotFoundError:
        print(f'\nNeed to create a key to encrypt local storage of API keys.')
        newCryptoKey = Fernet.generate_key()
        try:
            with open('config\\key.key', 'wb') as keyFile:
                keyFile.write(newCryptoKey)
                keyFile.close()
        except PermissionError:
            print(f'\nERROR:  Permission was denied when writing key file.')
        cryptoKey = newCryptoKey
    return cryptoKey


def encrypt_api_keys(message, cryptoKey):
    """
    Encrypt the API keys and return the data for writing to file.
    """
    f = Fernet(cryptoKey)
    encryptedMessage = f.encrypt(message.encode())
    return encryptedMessage


def decrypt_api_keys(message, cyrptoKey):
    """
    Decrypt the API keys and return them for use in memory.
    """
    f = Fernet(cyrptoKey)
    decryptedMessage = f.decrypt(message).decode()
    return decryptedMessage