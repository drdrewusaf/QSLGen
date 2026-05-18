"""
Write data through the QRZ API interface.
"""
from time import sleep

import requests

from qslgen import headers, today
from qslgen.logger import writer as log_writer


def payloadAdifSelector(qsodata):
    """
    Selects only the ADIF data we want to update on QRZ for each QSO.
    The keys identified below represent the minimum requirement and additional data that the author
    thought was pertinent to updating the QSO.
    :param qsodata: the current QSO being worked on
    :return payloadAdifData: a dict to update QRZ
    """
    payloadAdifKeys = {1: 'band',
                       2: 'call',
                       5: 'freq',
                       6: 'mode',
                       11: 'qso_date',
                       13: 'station_callsign',
                       14: 'time_on',
                       15: 'rst_sent',
                       16: 'tx_pwr',
                       17: 'comment',
                       18: 'notes'}
    payloadAdifData = ''
    for k in payloadAdifKeys.keys():
        if len(qsodata[k]) > 0:
            payloadAdifData = (payloadAdifData
                               + f'<'
                               + payloadAdifKeys[k]
                               + ':' + str(len(qsodata[k]))
                               + '>'
                               + qsodata[k])
    return payloadAdifData


def write_data(q, apiKey):
    """
    Writes the QSO data to QRZ's database using the REPLACE option via the QRZ API. As of this version, there is not an
    explicit UPDATE option through the QRZ API. So, REPLACE it is...
    Calls the payloadAdifSelector function on each QSO to send only certain data the author thought pertinent.
    :param q: the QSO being worked on
    :param apiKey: the API associated to the QSO being worked on
    """
    tryNum = 3
    while tryNum > 0:
        sleep(2)
        tryNum -= 1
        try:
            print('Updating QSO on QRZ.com to reflect eQSL sent.')
            payloadAdifData = payloadAdifSelector(q)
            updatePayload = {'KEY': f'{apiKey}',
                             'ACTION': 'INSERT',
                             'OPTION': 'REPLACE',
                             'ADIF': payloadAdifData +
                                    f'<eqsl_qsl_sent:1>Y'
                                    f'<eqsl_qslsdate:{len(today)}>{today}'
                                    f'<eor>'}
            url = 'https://logbook.qrz.com/api'
            insertResponse = requests.get(url, headers=headers, params=updatePayload)
            if 'REPLACE' not in insertResponse.text:
                log_writer(f'QRZ.com reported an error while updating the QSO with callsign {q[2]}.\n'
                           f'Here is the response:  {insertResponse.text}\n',
                           end=False)
                print(f'QRZ.com reported an error: {insertResponse.text}')
            else:
                print('QRZ.com QSO updated.')
            tryNum = 0
        except Exception as e:
            if tryNum > 0:
                print(f'\nThere was an error connecting to the server.  Will retry {tryNum} more times.'
                      f'\nError:  {e}')
            else:
                print(f'Too many connection errors. QSO not updated on QRZ. The QSO is recorded in the log'
                      f'so you can update it manually.')
                log_writer(f'QSO with {q[2]} on {q[11]} failed to update on QRZ. Too many connection errors.\n',
                           end=False)
