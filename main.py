import datetime
import os
import re

import adif_io
import html2text
# To use imgkit, you need to install wkhtmltopdf for your OS and add it to PATH.
import imgkit
import requests
import win32com.client as win32
from bs4 import BeautifulSoup

"""
Begin variables essential to the user.
**You MUST update the variables below for your personal use.**
"""
# These imgkit options are set for the size of my QSL card...change to your preference/background image size.
imgkitOptions = {
    'format': 'jpg',
    'crop-w': '1800',
    'crop-h': '1115',
    'enable-local-file-access': ''  # Do not remove this option; it will cause imgkit/wkhtmltoimage failure.
}
# Place your name in the variable below for the email signature.
myName = 'YourName'

# Place your QRZ.com logbook API keys, without dashes, in the apiKeys array variable below.
apiKeys = ['EXAMPLEKEY1',
           'EXAMPLEKEY2',
           'EXAMPLEKEY3']

"""
End user essential edits.
"""


def underScoreCheck(ixCall):
    """
    QRZ.com returns prefixed and suffixed callsigns with an underscore.
    This function returns it to a slash for the QSL card and email, and
    returns it to an underscore for filenames.
    """
    if '_' in ixCall:
        ixCall = ixCall.replace('_', '/')
    elif '/' in ixCall:
        ixCall = ixCall.replace('/', '_')
    else:
        return (ixCall)
    return (ixCall)


def logWriter(message, end=True):
    with open('log.txt', 'a') as log:
        log.write(f'{message}\n')
        if end:
            log.write('***********\n')
        log.close()


# These are the dictionary keys in the ADIF data we want to work with (QRZ sends many others)
wantedAdifKeys = ['APP_QRZLOG_LOGID', 'BAND', 'CALL', 'EMAIL', 'EQSL_QSL_SENT',
                  'FREQ', 'MODE', 'MY_CITY', 'MY_COUNTRY', 'MY_GRIDSQUARE', 'NAME',
                  'QSO_DATE', 'RST_RCVD', 'STATION_CALLSIGN', 'TIME_ON']

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

# Iterate through the user's API keys.
for ak in apiKeys:
    today = str(datetime.date.today())
    qsos = []
    reduxqsos = []
    print(f'\nGathering confimed QSOs since {dateSince} for logbook API key {ak}...')
    getPayload = {'KEY': f'{ak}', 'ACTION': 'FETCH', 'OPTION': f'MODSINCE:{dateSince},STATUS:CONFIRMED'}
    url = 'https://logbook.qrz.com/api'
    gr = requests.get(url, params=getPayload)
    # To fix errors in reading special characters, convert to ascii
    gr.encoding = 'ascii'
    data = html2text.html2text(gr.text)
    try:
        data_re = re.search('<', data).span()
    except:
        if 'invalid api key' in data:
            logWriter('Check your API Key. QRZ.com reported an invalid key.', end=False)
            print('Check your API Key. QRZ.com reported an invalid key.')
        else:
            logWriter('Regex search failed. Probably no confirmed QSOs since {dateSince}.\n'
                      f'API key: {ak}\n'
                      f'dateSince: {dateSince}\n'
                      f'data: {data}\n',
                      end=False)
            print(f'Regex search failed. Probably no confirmed QSOs since {dateSince}.')
        logWriter('')
        print(f'Here is the data the server returned: {data}', end='')
        continue
    else:
        cursor = data_re[0]
        data = data[cursor:]
        qsos = adif_io.read_from_string(data)[0]

    dataLen = len(qsos)
    if dataLen <= 0:
        continue
    else:
        for q in qsos:
            curr_qso = []
            keyCount = 0
            while keyCount < len(wantedAdifKeys):
                if wantedAdifKeys[keyCount] not in q.keys():
                    curr_qso.append('')
                    keyCount += 1
                else:
                    if keyCount == 2:
                        callDistantSlash = underScoreCheck(q[wantedAdifKeys[keyCount]])
                        curr_qso.append(callDistantSlash)
                    elif keyCount == 13:
                        callLocalSlash = underScoreCheck(q[wantedAdifKeys[keyCount]])
                        curr_qso.append(callLocalSlash)
                    else:
                        curr_qso.append(q[wantedAdifKeys[keyCount]])
                    keyCount += 1
            reduxqsos.append(curr_qso)

    # Array position reference: 0APP_QRZLOG_LOGID, 1BAND, 2CALL, 3EMAIL, 4EQSL_QSL_SENT,
    # 5FREQ, 6MODE, 7MY_CITY, 8MY_COUNTRY, 9MY_GRIDSQUARE, 10NAME, 11QSO_DATE,
    # 12RST_RCVD, 13STATION_CALLSIGN, 14TIME_ON
    qsoCount = 0
    while qsoCount < len(reduxqsos):
        if len(reduxqsos[qsoCount][3]) <= 0 or 'Y' in reduxqsos[qsoCount][4]:
            del reduxqsos[qsoCount]
        else:
            qsoCount += 1
    reduxDataLen = len(reduxqsos)
    if reduxDataLen <= 0:
        logWriter(f'Length of reduced data is {dataLen}.\n'
                  f'If there are any new confirmed QSOs since {dateSince},\n'
                  f'they likely do not have a public email address.',
                  end=True)
        print(f'If there are any new confirmed QSOs since {dateSince}, they likely do not '
              f'have a public email address.')
        continue
    print(f'Ready to generate and email QSL cards for {reduxDataLen} QSOs.\n'
          'Here is a list of callsigns we will QSL:')
    qsoCount = 0
    for q in reduxqsos:
        if qsoCount == reduxDataLen - 1:
            print(f'{q[2]}')
        else:
            print(f'{q[2]}, ', end='')
            qsoCount += 1
    # Give the user a chance to cancel based on the data QSLGen plans to use.
    yesno = input('Please confirm you want to send these QSL Cards *AND*\n'
                  'the Outlook desktop application is open. (Y/n): ').lower()
    if yesno == 'y' or yesno == 'yes' or not yesno:
        for q in reduxqsos:
            callLocalUnderscore = underScoreCheck(q[13])
            callDistantUnderscore = underScoreCheck(q[2])
            # The HTML file below is the template for the QSL Card. Edit the file as you see fit.
            with open('QSLGen.html') as templateFile:
                soup = BeautifulSoup(templateFile, 'html.parser')
            templateFile.close()
            idCount = 1
            while idCount < len(wantedAdifKeys):
                try:
                    soup.find_all(id=idCount)[0].string.replaceWith(q[idCount])
                    idCount += 1
                except IndexError:
                    idCount += 1
            soup.find_all(id='call')[0].string.replaceWith(q[13])
            soup.find_all(id='localStation')[0].string.replaceWith(f'{q[7]}, {q[8]}  {q[9]}')
            soup.find_all(id='thanks')[0].string.replaceWith(f'Thanks for the QSO! 73 de {q[13]}')
            soup.body['style'] = f"background-image: url('{callLocalUnderscore}_bg.jpg');"
            with open('Curr_QSLGen.html', 'w') as currQSL:
                currQSL.write(str(soup))
            currQSL.close()
            filenameQSLCard = f'{callDistantUnderscore} de {callLocalUnderscore}.jpg'
            imgkit.from_file('Curr_QSLGen.html', f'{filenameQSLCard}', options=imgkitOptions)
            print(f'Sending QSL card email to {q[2]}.')
            emailName = q[10].title()
            # Outlook needs to be opened by the user first
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = q[3]
            mail.Subject = f'QSL de {q[13]}'
            mail.Body = (f'Good Day {emailName} ({q[2]})!\n\n'
                         'Thank you for the QSO!  You will find my QSL card attached.  '
                         'The QSO is logged on QRZ and LOTW.\n'
                         'Hope to hear you on the air again soon!\n\n\n'
                         '73,\n'
                         f'{q[13]}\n'
                         f'{myName}\n\n'
                         '* This email was automatically generated and sent using the QSLGen Python script '
                         'by KF3OFP/DA6AJP: https://github.com/drdrewusaf/QSLGen *')
            attachment = f'{os.getcwd()}\\{filenameQSLCard}'
            mail.Attachments.Add(attachment)
            mail.Send()
            print('Email sent.')
            print('Deleting QSL card.')
            os.remove(filenameQSLCard)
            print(f'Updating QSO on QRZ.com to reflect eQSL sent.')
            # Array position reference again: 0APP_QRZLOG_LOGID, 1BAND, 2CALL, 3EMAIL, 4EQSL_QSL_SENT,
            # 5FREQ, 6MODE, 7MY_CITY, 8MY_COUNTRY, 9MY_GRIDSQUARE, 10NAME, 11QSO_DATE,
            # 12RST_RCVD, 13STATION_CALLSIGN, 14TIME_ON
            postPayload = {'KEY': f'{ak}', 'ACTION': 'INSERT', 'OPTION': 'REPLACE',
                           'ADIF': f'<band:{len(q[1])}>{q[1]}'
                                   f'<mode:{len(q[6])}>{q[6]}'
                                   f'<freq:{len(q[5])}>{q[5]}'
                                   f'<call:{len(q[2])}>{q[2]}'
                                   f'<qso_date:{len(q[11])}>{q[11]}'
                                   f'<station_callsign:{len(q[13])}>{q[13]}'
                                   f'<time_on:{len(q[14])}>{q[14]}'
                                   f'<eqsl_qsl_sent:1>Y'
                                   f'<eqsl_qslsdate:{len(today)}>{today}'
                                   f'<eor>'}
            url = 'https://logbook.qrz.com/api'
            pr = requests.post(url, params=postPayload)
            if 'FAIL' in pr.text:
                with open('log.txt', 'a') as log:
                    logWriter(f'QRZ.com reported an error while updating the QSO'
                              f' with callsign {q[2]}.\n'
                              f'Here is the response:  {pr.text}\n',
                              end=True)
                print(f'QRZ.com reported an error: {pr.text}')
            else:
                print('QRZ.com QSO updated.')
    elif yesno == 'n' or yesno == 'no':
        print('You have declined to send the QSLs listed above.\n')
        if len(apiKeys) > 1:
            print('Moving on to the next API key.')
        continue
    else:
        # FIXME: this just moves on, but should give the user another chance
        print('Invalid input.')
        continue

print('QSLGen finished sending and updating okayed QSLs for all confirmed QSOs since\n'
      f'{dateSince} using the provided API keys.\n'
      'You should check your email sent items and QRZ.com to ensure everything\n'
      'processed as expected.')
exit(0)
