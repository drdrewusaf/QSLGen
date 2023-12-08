import datetime
import os
import re

import adif_io
import html2text
import requests
import win32com.client as win32

# To use imgkit, you need to install wkhtmltopdf for your OS and add it to PATH.
import imgkit
from bs4 import BeautifulSoup

qsos = []
reduxqsos = []
"""
Begin user essntial edits.
Update the variables below for your personal use.
"""
# These options are set for the size of my QSL card...change to your preference.
imgkitOptions = {
    'format': 'jpg',
    'crop-w': '1800',
    'crop-h': '1115',
    'enable-local-file-access':''  # Do not remove this option; it will cause imgkit/wkhtmltoimage failure.
}
# PLace your calsign in the variable below.
myCall = 'CALLSIGN'
# Place your name in the variable below.
myName = 'Name'
# Place your QRZ.com logbook API keys, without dashes, in the apiKeys array variable below.
apiKeys = ['EXAMPLEKEY1',
           'EXAMPLEKEY2',
           'EXAMPLEKEY3']
"""
End user essntial edits.
"""
wantedKeys = ['BAND', 'CALL', 'EMAIL', 'FREQ', 'MODE', 'NAME', 'QSO_DATE', 'RST_RCVD', 'TIME_OFF']
try:
    dateSince = datetime.date.fromtimestamp(os.path.getmtime('Curr_QSLGen.html'))
except FileNotFoundError:
    print('Could not find Curr_QSLGen.html file. Assuming this is the first run.\n'
          'This program uses the last modified date of the Curr_QSLGen.html file to\n'
          'determine which QSOs to download. Since that file does not exist, please \n'
          'provide the first date from which to gather confirmed QSOs. After this\n'
          'first run, the Curr_QSLGen.html file should not be deleted or modified by\n'
          'anything other than this script. As long as the file exists, you will not\n'
          'be asked for a date again. Suggest using a relatively recent date.\n')
    dateSince = input('Please provide your desired date in the YYYY-MM-DD format:  ')

for k in apiKeys:
    print(f'Gathering confimed QSOs since {dateSince} for logbook API key {k}...')
    payload = {'KEY':f'{k}', 'ACTION':'FETCH', 'OPTION': f'MODSINCE:{dateSince}, STATUS:CONFIRMED'}
    url = 'https://logbook.qrz.com/api'
    r = requests.get(url, params=payload)
    data = html2text.html2text(r.text)
    try:
        data_re = re.search('<', data).span()
    except:
        with open('log.txt', 'a') as log:
            log.write(f'API Key: {k}\n'
                      f'Date since: {dateSince}\n'
                      f'Data: \n{data}'
                      'Regex failed. Probably no new confirmed QSOs.\n'
                      '***********\n')
            log.close()
        if 'invalid api key' in data:
            print(f'Check your API Key. QRZ.com reported an invalid key.')
        else:
            print(f'Regex failed. Probably no confirmed QSOs since {dateSince}.')
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
                  f'No new confirmed QSOs since {dateSince}.\n'
                  '***********\r\n')
        log.close()
    print(f'No new confirmed QSOs since {dateSince}.')
else:
    for i in qsos:
        curr_qso = []
        keyCount = 0
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

for q in reduxqsos:
    if len(q[2]) > 0:
        with open('QSLGen.html') as templateFile:
            soup = BeautifulSoup(templateFile, 'html.parser')
        templateFile.close()
        idCount = 0
        while idCount < 9:
            try:
                soup.find_all(id=idCount)[0].string.replaceWith(q[idCount])
                idCount += 1
            except IndexError:
                idCount += 1
        soup.b.string.replaceWith(f'Thanks for the QSO! 73 de {myCall}')
        with open('Curr_QSLGen.html', 'w') as currQSL:
            currQSL.write(str(soup))
        currQSL.close()
        filenameQSLCard = f'{q[1]} de {myCall}.jpg'
        imgkit.from_file('Curr_QSLGen.html',filenameQSLCard, options=imgkitOptions)
        print(f'Sending QSL card email to {q[1]}.')
        if " " in q[5]:
            emailName = q[5].split(" ")[0]
        else:
            emailName = q[5]
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = q[2]
        mail.Subject = f'QSL de {myCall}'
        mail.Body = (f'Good Day {emailName} ({q[1]})!\n\n'
                     'Thank you for the QSO!  You will find my QSL card attached.  The QSO is logged on QRZ and LOTW.\n'
                     'Hope to hear you on the air again soon!\n\n\n'
                     '73,\n'
                     f'{myCall}\n'
                     f'{myName}\n\n'
                     '*This email was automatically generated and sent using my QSLGen Python script: '
                     'https://github.com/drdrewusaf/QSLGen *')
        attachment = f'{os.getcwd()}\\{filenameQSLCard}'
        mail.Attachments.Add(attachment)
        mail.Send()
        print('Email sent.')
        print('Deleting QSL card.')
        os.remove(filenameQSLCard)
    else:
        pass
exit(0)
