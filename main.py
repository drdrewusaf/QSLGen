import requests
import html2text
import adif_io
import re
import datetime
import xlsxwriter
import string

qsos = []
reduxqsos = []
wantedKeys = ['KEY','BAND','CALL','EMAIL','FREQ','MODE','NAME','QSO_DATE','RST_RCVD','TIME_OFF']
headerCount = len(wantedKeys)
headerLetter = list(string.ascii_uppercase)[headerCount - 1]
datesince = datetime.date.today()
"""
Replace *APIKEY* in the payload variable below with your QRZ.com API key without dashes.
"""
payload = {'KEY': '*APIKEY*', 'ACTION': 'FETCH', 'OPTION': f'MODSINCE:{datesince},STATUS:CONFIRMED'}
url = 'https://logbook.qrz.com/api'
r = requests.get(url, params=payload)
data = html2text.html2text(r.text)
try:
    data_re = re.search('<', data).span()
except:
    print(data)
    print('Regex failed. Probably no new confirmed QSOs.')
    exit(0)
cursor = data_re[0]
data = data[cursor:]
qsos = adif_io.read_from_string(data)[0]
dataLen = len(qsos)

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
            if keyCount < len(wantedKeys)-1:
                keyCount += 1
    reduxqsos.append(curr_qso)
    tblKey += 1

workbook = xlsxwriter.Workbook('QSOs.xlsx')
worksheet = workbook.add_worksheet()
worksheet.add_table(f'A1:{headerLetter}{dataLen}', {'name': 'QSOS',
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
exit(0)