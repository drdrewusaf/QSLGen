import json

from qslgen import crypto
from qslgen import oauthFile

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


def build_service():
    flow = InstalledAppFlow.from_client_config(read_oauth_data(),
                                               scopes=['https://www.googleapis.com/auth/gmail.send'])
    credentials = flow.run_local_server(host='localhost',
                                        port=8080,
                                        authorization_prompt_message='Please visit this URL: {url}',
                                        success_message='The auth flow is complete; you may close this window.',
                                        open_browser=True)
    return build('gmail', 'v1', credentials=credentials)


def read_oauth_data():
    cryptoKey = crypto.load_crypto_key()
    try:
        with open(oauthFile, 'rb') as f:
            decryptedFile = crypto.decrypt_data(f.read(), cryptoKey)
            if len(decryptedFile) > 0:
                oauth_data = json.loads(decryptedFile)
                f.close()
            else:
                print(f'\nNo OAuth data found. Please use the settings menu to update your email address and '
                      f'follow the README to create your OAuth credentials.')
    except FileNotFoundError:
        print(f'\nNo OAuth data found. Please use the settings menu to update your email address and '
              f'follow the README to create your OAuth credentials.')
    return oauth_data


def write_oauth_data(oauth_str):
    cryptoKey = crypto.load_crypto_key()
    try:
        with open(oauthFile, 'wb') as f:
            encryptedFile = crypto.encrypt_data(oauth_str, cryptoKey)
            f.write(encryptedFile)
        f.close()
    except PermissionError:
        print(f'\nERROR:  Permission was denied when writing OAuth JSON file.')