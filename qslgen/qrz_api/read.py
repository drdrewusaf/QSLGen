"""
Read data through the QRZ API interface.
"""
import re
import requests
import html2text
import adif_io

from qslgen import headers as head
from qslgen.logger import writer as log_writer
from time import sleep


def request_data(apiKey, dateSince):
    tryNum = 3
    qsos = []
    print(f'Gathering confirmed QSOs since {dateSince} for logbook API key {apiKey}...')
    getPayload = {'KEY': f'{apiKey}',
                  'ACTION': 'FETCH',
                  'OPTION': f'MODSINCE:{dateSince},STATUS:CONFIRMED'}
    headers = head
    url = 'https://logbook.qrz.com/api'
    while tryNum > 0:
        sleep(2)
        tryNum -= 1
        try:
            fetchResponse = requests.get(url, headers=headers, params=getPayload)
            # To fix errors in reading special characters, convert to ascii
            fetchResponse.encoding = 'ascii'
            data = html2text.html2text(fetchResponse.text)
            try:
                data_re = re.search('<', data).span()
                cursor = data_re[0]
                data = data[cursor:]
                qsos = adif_io.read_from_string(data)[0]
            except:
                if 'invalid api key' in data:
                    log_writer('Check your API Key. QRZ.com reported an invalid key.', end=False)
                    print('Check your API Key. QRZ.com reported an invalid key.')
                else:
                    log_writer(f'Regex search failed. Probably no confirmed QSOs since {dateSince}.\n'
                               f'API key: {apiKey}\n'
                               f'dateSince: {dateSince}\n'
                               f'data: {data}\n',
                               end=False)
                    print(f'Regex search failed. Probably no confirmed QSOs since {dateSince}.')
                    log_writer('')
                    print(f'Here is the data the server returned: {data}')
            tryNum = 0
        except Exception as e:
            if tryNum > 0:
                print(f'\nThere was an error connecting to the server.  Will retry {tryNum} more times.'
                      f'\nError:  {e}')
            else:
                print(f'Too many connection errors. Returning to main menu.')
                return 'error'
    return qsos
