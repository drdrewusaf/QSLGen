"""
Read data through the QRZ API interface.
"""
import re
from time import sleep

import adif_io
import html2text
import requests

from qslgen import headers as head
from qslgen.logger import writer as log_writer


def request_data(apiKey, dateSince):
    """
    Requests QSOs associated with the current API key and since the date requested by the user (either explicitly, or
    based on the previous run).
    :param apiKey: the current API key being worked on
    :param dateSince: the date from which to request QSOs - based on the date in the settings json file
    :return: QSOs that meet the API key and date since criteria, if any
    """
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
                    log_writer('Check your API Key. QRZ.com reported an invalid key.\n', end=False)
                    print('Check your API Key. QRZ.com reported an invalid key.')
                else:
                    log_writer(f'Regex search failed. Probably no confirmed QSOs since {dateSince}.\n'
                               f'API key: {apiKey}\n'
                               f'dateSince: {dateSince}\n'
                               f'data: {data}\n',
                               end=False)
                    print(f'Regex search failed. Probably no confirmed QSOs since {dateSince}.')
                    print(f'Here is the data the server returned: {data}')
            tryNum = 0
        except Exception as e:
            if tryNum > 0:
                print(f'\nThere was an error connecting to the server.  Will retry {tryNum} more times.'
                      f'\nError:  {e}')
            else:
                print(f'Too many connection errors.')
                return 'connError'
    return qsos
