import datetime
import os
import re
import string

import adif_io
import html2text
import requests
import win32com.client as win32
import xlsxwriter

qsos = []
reduxqsos = []
"""
Place your QRZ.com logbook API keys, without dashes, in the apiKeys array variable below.
"""
apiKeys = ['EXAMPLEKEY1',
           'EXAMPLEKEY2',
           'EXAMPLEKEY3']
wantedKeys = ['KEY', 'BAND', 'CALL', 'EMAIL', 'FREQ', 'MODE', 'NAME', 'QSO_DATE', 'RST_RCVD', 'TIME_OFF']
xlsxHeaderCount = len(wantedKeys)
xlsxHeaderLetter = list(string.ascii_uppercase)[xlsxHeaderCount - 1]
try:
    datesince = datetime.date.fromtimestamp(os.path.getmtime('QSOs.xlsx'))
except FileNotFoundError:
    print('Could not find QSO.xlsx file. Assuming this is the first run.\n'
          'This program uses the last modified date of the QSO.xlsx file to determine\n'
          'which QSOs to download. Since that file does not exist, please provide the\n'
          'first date from which to gather confirmed QSOs. After this first run the\n'
          'QSO.xlsx file should only be edited to delete all table rows after you have\n'
          'processed your QSOs. As long as the file exists, you will not be asked for\n'
          'a date again. Suggest using a relatively recent date.\n')
    datesince = input('Please provide your desired date in the YYYY-MM-DD format:  ')

for k in apiKeys:
    print(f'Gathering confimed QSOs since {datesince} for logbook API key {k}...')
    payload = {'KEY':f'{k}', 'ACTION':'FETCH', 'OPTION': f'MODSINCE:{datesince}, STATUS:CONFIRMED'}
    url = 'https://logbook.qrz.com/api'
    r = requests.get(url, params=payload)
    data = html2text.html2text(r.text)
    try:
        data_re = re.search('<', data).span()
    except:
        with open('log.txt', 'a') as log:
            log.write(f'API Key: {k}\n'
                      f'Datesince: {datesince}\n'
                      f'Data: \n{data}'
                      'Regex failed. Probably no new confirmed QSOs.\n'
                      '***********\n')
            log.close()
        if 'invalid api key' in data:
            print(f'Check your API Key. QRZ.com reported an invalid key.')
        else:
            print(f'Regex failed. Probably no confirmed QSOs since {datesince}.')
        print(f'Here is the data the server returned: {data}')

    else:
        cursor = data_re[0]
        data = data[cursor:]
        adifData = adif_io.read_from_string(data)[0]
        if len(qsos) > 0:
            qsos.append(adifData[0])
        else:
            qsos = adifData

dataLen = len(qsos)
if dataLen <= 0:
    with open('log.txt', 'a') as log:
        log.write(f'Length of data is {dataLen}.\n'
                  f'No new confirmed QSOs since {datesince}.\n'
                  '***********\r\n')
        log.close()
    print(f'No new confirmed QSOs since {datesince}.')
else:
    tblKey = 1
    for i in qsos:
        curr_qso = []
        keyCount = 1
        curr_qso.append(tblKey)
        for k in i:
            if wantedKeys[keyCount] not in i.keys():
                curr_qso.append('')
                if keyCount < len(wantedKeys) - 1:
                    keyCount += 1
            elif k in wantedKeys[keyCount]:
                curr_qso.append(i[k])
                if keyCount < len(wantedKeys) - 1:
                    keyCount += 1
        reduxqsos.append(curr_qso)
        tblKey += 1
    """
    Create an Excel spreadsheet with the downloaded QSOs.
    """
    workbook = xlsxwriter.Workbook('QSOs.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.add_table(f'A1:{xlsxHeaderLetter}{dataLen}', {'name': 'QSOS',
                                                        'data': reduxqsos,
                                                        'columns': [{'header': wantedKeys[0]},
                                                                    {'header': wantedKeys[1]},
                                                                    {'header': wantedKeys[2]},
                                                                    {'header': wantedKeys[3]},
                                                                    {'header': wantedKeys[4]},
                                                                    {'header': wantedKeys[5]},
                                                                    {'header': wantedKeys[6]},
                                                                    {'header': wantedKeys[7]},
                                                                    {'header': wantedKeys[8]},
                                                                    {'header': wantedKeys[9]}
                                                                    ]})
    workbook.close()
    print('Success!\n')
    print(f'QSOs since {datesince} were written to QSO.xlsx in the same directory as this program.\n\n')
    print('Sending email to trigger Power Automate.')
    """
    Send an email to trigger the Power Automate flow.
    """
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    """
    Replace email address here with the one you use to trigger Power Automate.
    """
    mail.To = 'email@email.com'
    mail.Subject = f'QSLGen QSOs {datetime.date.today()}'
    mail.Body = 'QSO file created and ready for Power Automate to process.'
    mail.Send()
    print('Email sent.')
exit(0)
