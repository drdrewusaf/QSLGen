"""
Write data through the QRZ API interface.
"""
import requests
from qslgen import headers, today
from qslgen.logger import writer as log_writer


def payloadAdifSelector(qsodata):
    """
    Here we are building the payload to go along with the QSO update on QRZ.com.
    This is planned to expand to the full ADIF spec, but for now only updates
    the fields listed below.
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
        log_writer(f'QRZ.com reported an error while updating the QSO'
                   f' with callsign {q[2]}.\n'
                   f'Here is the response:  {insertResponse.text}\n',
                   end=True)
        print(f'QRZ.com reported an error: {insertResponse.text}')
    else:
        print('QRZ.com QSO updated.')
