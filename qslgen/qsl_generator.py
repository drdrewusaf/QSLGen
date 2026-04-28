import datetime
import os
from pathlib import Path

# To use imgkit, you need to install wkhtmltopdf for your OS and add it to PATH.
import imgkit
from bs4 import BeautifulSoup

import qso_processor
from logger import writer as log_writer
from qrz_api import read as api_read
from qrz_api import write as api_write
from qslgen import configDir
from qslgen import emailer
from qslgen import oauth
from qslgen import qslFilesDir
from qslgen import wantedAdifKeys
from qso_processor import underscore_check


def ask_to_generate(sendOrSave):
    validInputs = ['y', 'yes', 'n', 'no', '']
    valid = False
    while not valid:
        yesno = input(f'\nConfirm you want to generate and {sendOrSave} these QSL Cards. (Y/n): ').lower()
        if yesno in validInputs:
            if 'n' or 'no' in yesno:
                return False
            else:
                return True
        else:
            print('\nInvalid input.')
            yesno = ''


def generateQSLs(qsos, apiKey, imgkitOptions, myName, sendOrSave, keepQSLCard, updateQRZ, todayDir, service):
    generatedQSLs = 0
    htmlFile = Path.joinpath(qslFilesDir,'QSLGen.html')
    for q in qsos:
        callLocalUnderscore = underscore_check(q[13])
        callDistantUnderscore = underscore_check(q[2])
        # The HTML file below is the template for the QSL Card. Edit the file as you see fit.
        bgImageFile = Path.joinpath(qslFilesDir, 'bg_images', f'{callLocalUnderscore}_bg.jpg')
        with open(htmlFile) as templateFile:
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
        soup.body['style'] = f"background-image: url('{bgImageFile}');"
        with open(htmlFile, 'w') as currQSL:
            currQSL.write(str(soup))
        currQSL.close()
        filename = f'{callDistantUnderscore} de {callLocalUnderscore}'
        oPath = Path.joinpath(todayDir, f'{filename}.jpg')
        imgkit.from_file(htmlFile,
                         oPath,
                         options=imgkitOptions)
        emailer.generate_email(sendOrSave, todayDir, filename, myName, q, service)
        if keepQSLCard == 'DELETE':
            print('Deleting QSL card.')
            os.remove(oPath)
        if updateQRZ == 'YES':
            api_write.write_data(q, apiKey)
        generatedQSLs += 1
    return generatedQSLs


def generator_main(settings, apiKeys):
    dateSince = datetime.date.fromisoformat(settings['dateSince'])
    todayDir = Path.joinpath(configDir, 'cards', f'{settings['dateSince']}')
    try:
        os.mkdir(todayDir)
    except FileExistsError:
        pass
    except PermissionError:
        print(f'Permission denied while making directory {todayDir}')
    generatedQSLs = 0
    apiKeyCount = 0
    imgkitOptions = settings['imgkitOptions']
    service = oauth.build_service()

    for ak in apiKeys:
        qso_data = api_read.request_data(ak, dateSince)
        if len(qso_data) > 0:
            if qso_data == 'error':
                return generatedQSLs
            selected_qsos = qso_processor.processor(qso_data, dateSince)
            selected_qsos_len = len(selected_qsos)
            if selected_qsos_len <= 0:
                log_writer(f'Length of reduced data is {selected_qsos_len}.\n'
                           f'If there are any new confirmed QSOs since {dateSince},\n'
                           f'they likely do not have a public email address.',
                           end=True)
                print(f'If there are any new confirmed QSOs since {dateSince}, they likely do not '
                      f'have a public email address.')
                continue
            else:
                print(f'\nReady to generate and email QSL cards for {selected_qsos_len} QSOs.\n'
                      f'Here is a list of callsigns we will QSL:')
                qsoCount = 0
                for q in selected_qsos:
                    if qsoCount == selected_qsos - 1:
                        print(f'{q[2]}')
                    else:
                        print(f'{q[2]}, ', end='')
                        qsoCount += 1
                yesno = ask_to_generate(settings['email'])
                if yesno:
                    generatedQSLs = generatedQSLs + generateQSLs(selected_qsos,
                                                                 ak,
                                                                 imgkitOptions,
                                                                 settings['myName'],
                                                                 settings['email'],
                                                                 settings['keepQSLCard'],
                                                                 settings['updateQRZ'],
                                                                 todayDir,
                                                                 service)
                else:
                    print('You have declined to send the QSLs listed above.\n')
                apiKeyCount += 1
                if len(apiKeys) - 1 < apiKeyCount:
                    print(f'Moving on to next API key.')
    if settings['keepQSLCard'] == 'DELETE' and generatedQSLs > 0:
        os.remove(todayDir)
    return generatedQSLs
