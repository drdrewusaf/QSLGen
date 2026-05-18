"""
Gather QSO data from QRZ, process it, generate QSL cards, send/save them.
"""
import datetime
import os
from pathlib import Path

from bs4 import BeautifulSoup
from html2image import Html2Image

import qso_processor
from logger import writer as log_writer
from qrz_api import read as api_read
from qrz_api import write as api_write
from qslgen import emailer
from qslgen import oauth
from qslgen import qslFilesDir
from qslgen import wantedAdifKeys
from qso_processor import underscore_check


def ask_to_generate(sendOrSave):
    """
    Give the user the option to eQSL the reduced QSOs or not.
    :param sendOrSave: here to print on screen for the user to know if QSLgen is set to send or save the QSL card
    """
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


def generateQSLs(qsos, apiKey, imgOptions, myName, sendOrSave, keepQSLCard, updateQRZ, todayDir, service):
    """
    Generate the QSL card image file via Beautiful Soup 4 HTML edits and Html2Image. Then generate either an .eml file
    on local storage for sending later, or send an email message via Gmail OAuth API.
    :param qsos: dict of processed QSOs
    :param apiKey: current QRZ API key being worked on
    :param imgOptions: dict for height, width, and format of QSL card image file
    :param myName: user setting for their name in the email
    :param sendOrSave: user setting to send an email via Gmail or save an .eml file to send later
    :param keepQSLCard: user setting to keep the QSL card image file
    :param updateQRZ: user setting to update QRZ or not
    :param todayDir: local directory for this session's QSLs based on today's date
    :param service: Gmail OAuth API session or null
    :return generatedQSLs: number of QSLs for this API key
    """
    generatedQSLs = 0
    htmlFile = Path.joinpath(qslFilesDir, 'QSLGen.html')
    for q in qsos:
        callLocalUnderscore = underscore_check(q[13])
        callDistantUnderscore = underscore_check(q[2])
        bgImageFile = Path.joinpath(qslFilesDir, 'bg_images', f'{callLocalUnderscore}_bg.jpg')
        if not Path.exists(bgImageFile):
            print(f'The background image {callLocalUnderscore}_bg.jpg could not be found.')
            exit(1)
        # The HTML file below is the template for the QSL Card. Edit the file as you see fit.
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
        qslCard = Path.joinpath(todayDir, f'{filename}.jpg')
        qslCardImage = Html2Image(size=(imgOptions['width'], imgOptions['height']), output_path=todayDir)
        qslCardImage.screenshot(html_file=htmlFile, save_as=filename)

        # Generate an email either for sending or saving
        emailer.generate_email(sendOrSave, todayDir, qslCard, filename, myName, q, service)
        if keepQSLCard == 'DELETE':
            print('Deleting QSL card.')
            os.remove(qslCard)
        if updateQRZ == 'YES':
            api_write.write_data(q, apiKey)
        generatedQSLs += 1
    return generatedQSLs


def generator_main(settings, apiKeys):
    """
    Main QSO/QSL logic. Reads data from QRZ using all saved API keys and iterates through all QSOs to generate
    QSL cards. Based on user settings, will send emails via Gmail OAuth API os save them locally.
    :param settings: user settings dict from settings.json file
    :param apiKeys: list of user-provided API key(s)
    :return generatedQSLs: number of QSLs sent during this session
    """
    dateSince = datetime.date.fromisoformat(settings['dateSince'])
    todayDir = Path.joinpath(Path(__file__).parent, 'cards', f'{settings['dateSince']}')
    try:
        os.mkdir(todayDir)
    except FileExistsError:
        pass
    except PermissionError:
        print(f'Permission denied while making directory {todayDir}')
    generatedQSLs = 0
    apiKeyCount = 0
    imgOptions = settings['html2image']

    # Create an OAuth session with Gmail API if the user selected to send the emails from QSLGen
    if settings['email'] == 'SEND':
        service = oauth.build_service()
    else:
        service = ''

    # Iterate through user-provided API keys and associated QSOs
    for ak in apiKeys:
        # Gather QSOs from QRZ through the API
        qso_data = api_read.request_data(ak, dateSince)
        if len(qso_data) > 0:
            if qso_data == 'connError':
                # If we tried to read 3 times, but they all failed, return
                print(f'Connection failure with API key {ak}.')
                return generatedQSLs
            # Reduce the QSOs to actionable and pertinent data
            selected_qsos = qso_processor.processor(qso_data, dateSince)
            selected_qsos_len = len(selected_qsos)
            if selected_qsos_len <= 0:
                log_writer(f'Length of reduced data for API key {ak} is {selected_qsos_len}.\n'
                           f'If there are any new confirmed QSOs since {dateSince}, '
                           f'they likely do not have a public email address.\n',
                           end=False)
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
                                                                 imgOptions,
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
