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
myName = 'Your Name'

"""
End user essential edits.
"""
apiKeys = []


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


def askToGenerate():
    validInputs = ['y', 'yes', 'n', 'no']
    valid = False
    while not valid:
        yesno = input('Please confirm you want to generate/send these QSL Cards *AND*\n'
                      'the Outlook desktop application is open. (Y/n): ').lower()
        # Default to yes.
        if not yesno:
            yesno = 'y'
            valid = True
        elif yesno in validInputs:
            valid = True
        else:
            print('Invalid input.')
            yesno = ''
    return (yesno)


def payloadAdifSelector(qsodata):
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


def generateQSLs(reduxqsos):
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
        # 12RST_RCVD, 13STATION_CALLSIGN, 14TIME_ON, 15RST_SENT, 16TX_PWR, 17COMMENT, 18NOTES
        payloadAdifData = payloadAdifSelector(q)
        updatePayload = {'KEY': f'{ak}',
                         'ACTION': 'INSERT',
                         'OPTION': 'REPLACE',
                         'ADIF': payloadAdifData +
                         f'<eqsl_qsl_sent:1>Y'
                         f'<eqsl_qslsdate:{len(today)}>{today}'
                         f'<eor>'}

        url = 'https://logbook.qrz.com/api'
        insertResponse = requests.get(url, params=updatePayload)
        if 'REPLACE' not in insertResponse.text:
            with open('log.txt', 'a') as log:
                logWriter(f'QRZ.com reported an error while updating the QSO'
                          f' with callsign {q[2]}.\n'
                          f'Here is the response:  {insertResponse.text}\n',
                          end=True)
            print(f'QRZ.com reported an error: {insertResponse.text}')
        else:
            print('QRZ.com QSO updated.')


def addApiKeys():
    addedKeys = []
    finished = False
    print('QSLGen will now ask you to input your API key(s) one at a time and\n'
          'save them in apikeys.txt in this running directory.')
    while not finished:
        newKey = input("Please enter one API key, with or without dashes, or type 'done' to finish.\n"
                       "New API key: ")
        if newKey == 'done':
            finished = True
        elif re.match('(\\d|[A-z]){4}(-?)(\\d|[A-z]){4}(-?)(\\d|[A-z]){4}(-?)(\\d|[A-z]){4}(-?)', newKey):
            addedKeys.append(newKey)
        else:
            print('Invalid key.')
    if len(addedKeys) > 0:
        return (addedKeys)


def editApiKeyFile():
    finished = False
    editsDone = False
    newKeys = []
    while not finished:
        if os.path.isfile('apikeys.txt'):
            with open('apikeys.txt', 'r') as f:
                fKeys = f.read()
                if len(fKeys) > 0:
                    newKeys = fKeys.split(',')
            f.close()
            while not editsDone:
                count = 0
                print('API keys currently in file and memory:\n')
                for k in newKeys:
                    print('[' + str(count) + ']: ' + ' ' + k)
                    count += 1
                opt = input('Options:\n'
                            '[0-n]: Delete key by id above.\n'
                            '[A]: Add new key(s).\n'
                            '[D]: Done. Return to main.\n'
                            'Please enter your option: ').lower()
                if opt.isnumeric():
                    try:
                        newKeys.pop(int(opt))
                    except IndexError:
                        print('Invalid key id.')
                elif opt == 'd':
                    editsDone = True
                elif opt == 'a':
                    addedApiKeys = addApiKeys()
                    if len(addedApiKeys) > 0:
                        for k in addedApiKeys:
                            newKeys.append(k)
                    print(f'Added {len(addedApiKeys)} keys.')
                else:
                    print('Invalid input.')
        else:
            print('No apikeys.txt file found.  Will generate one now.')
            newKeys = addApiKeys()
        if not newKeys:
            input('I cannot continue without at least one API key.\n'
                  'Press Enter to exit.')
            exit(0)
        else:
            finished = True
    with open('apikeys.txt', 'w') as f:
        count = 0
        for k in newKeys:
            if count == len(newKeys) - 1:
                f.write(k)
            else:
                f.write(k + ',')
                count += 1
    return (newKeys)


def mainMenu():
    global apiKeys
    validInputs = ['g', 'u', 'q']
    valid = False
    while not valid:
        opt = input('Welcome to QSLGen.\n\n'
                    'Please select from the following options:\n'
                    '[G]: Generate QSLs now.\n'
                    '[U]: Update or create your apikey.txt file.\n'
                    '[Q]: Quit.\n'
                    'Please type your selection and press enter: ').lower()
        if opt in validInputs:
            valid = True
        else:
            print('Invalid input.')
    if opt == 'q':
        print('See you next time!')
        exit(0)
    elif opt == 'u':
        apiKeys = editApiKeyFile()
    elif opt == 'g':
        try:
            with open('apikeys.txt') as f:
                apiKeys = f.read().split(',')
            f.close()
        except FileNotFoundError:
            apiKeys = editApiKeyFile()
        if len(apiKeys) == 0:
            print('The apikeys.txt file seems to be empty.\n')
            apiKeys = editApiKeyFile()


# Get things started.
mainMenu()

# These are the dictionary keys in the ADIF data we want to work with (QRZ sends many others)
wantedAdifKeys = ['APP_QRZLOG_LOGID', 'BAND', 'CALL', 'EMAIL', 'EQSL_QSL_SENT',
                  'FREQ', 'MODE', 'MY_CITY', 'MY_COUNTRY', 'MY_GRIDSQUARE', 'NAME',
                  'QSO_DATE', 'RST_RCVD', 'STATION_CALLSIGN', 'TIME_ON', 'RST_SENT', 'TX_PWR',
                  'COMMENT', 'NOTES']

try:
    dateSince = datetime.date.fromtimestamp(os.path.getmtime('Curr_QSLGen.html'))
except FileNotFoundError:
    needDate = True
    while needDate:
        print('Could not find Curr_QSLGen.html file. Assuming this is the first run.\n'
              'This program uses the last modified date of the Curr_QSLGen.html file to\n'
              'determine which QSOs to download. Since that file does not exist, please \n'
              'provide the first date from which to gather confirmed QSOs. After this\n'
              'first run, the Curr_QSLGen.html file should not be deleted or modified by\n'
              'anything other than this script. As long as the file exists, you will not\n'
              'be asked for a date again. Suggest using a relatively recent date.\n')
        dateSince = input('Please provide your desired date in the YYYY-MM-DD format:  ')
        if re.match('^(\\d){4}-(\\d){2}-(\\d){2}', dateSince):
            needDate = False
        else:
            print('Invalid format.')

# Iterate through the user's API keys.
for ak in apiKeys:
    today = str(datetime.date.today()).replace('-', '')
    qsos = []
    reduxqsos = []
    print(f'\nGathering confimed QSOs since {dateSince} for logbook API key {ak}...')
    getPayload = {'KEY': f'{ak}',
                  'ACTION': 'FETCH',
                  'OPTION': f'MODSINCE:{dateSince},STATUS:CONFIRMED'}

    url = 'https://logbook.qrz.com/api'
    fetchResponse = requests.get(url, params=getPayload)
    # To fix errors in reading special characters, convert to ascii
    fetchResponse.encoding = 'ascii'
    data = html2text.html2text(fetchResponse.text)
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
    # 12RST_RCVD, 13STATION_CALLSIGN, 14TIME_ON, 15RST_SENT, 16TX_PWR, 17COMMENT, 18NOTES
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
    yesno = askToGenerate()
    if yesno == 'y' or yesno == 'yes':
        generateQSLs(reduxqsos)
    elif yesno == 'n' or yesno == 'no':
        print('You have declined to send the QSLs listed above.\n')
        if len(apiKeys) > 1:
            print('Moving on to the next API key.')
        continue

print('QSLGen finished sending and updating okayed QSLs for all confirmed QSOs since\n'
      f'{dateSince} using the provided API keys.\n'
      'You should check your email sent items and QRZ.com to ensure everything\n'
      'processed as expected.')
exit(0)
