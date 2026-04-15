import os

# To use imgkit, you need to install wkhtmltopdf for your OS and add it to PATH.
import imgkit
import win32com.client as win32
from qslgen import wantedAdifKeys
from bs4 import BeautifulSoup
from qso_processor import underscore_check
from qrz_api import write as api_write

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
generatedQSLs = 0


def ask_to_generate():
    validInputs = ['y', 'yes', 'n', 'no', '']
    valid = False
    while not valid:
        yesno = input('\nConfirm the **Outlook desktop application is open** in the background, \n'
                      'and you want to generate and send these QSL Cards. (Y/n): ').lower()
        # Default to yes if the user just presses enter.
        if yesno in validInputs:
            valid = True
        else:
            print('\nInvalid input.')
            yesno = ''
    return yesno


def generateQSLs(qsos, apiKey):
    """
    This is where we generate the QSL card and email, then send it using the
    Microsoft Outlook application.
    """
    generatedQSLs = 0
    for q in qsos:
        callLocalUnderscore = underscore_check(q[13])
        callDistantUnderscore = underscore_check(q[2])
        # The HTML file below is the template for the QSL Card. Edit the file as you see fit.
        with open('config\\qsl\\QSLGen.html') as templateFile:
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
        soup.body['style'] = f"background-image: url('bg_images\\{callLocalUnderscore}_bg.jpg');"
        with open('config\\qsl\\Curr_QSLGen.html', 'w') as currQSL:
            currQSL.write(str(soup))
        currQSL.close()
        filenameQSLCard = f'{callDistantUnderscore} de {callLocalUnderscore}.jpg'
        imgkit.from_file('config\\qsl\\Curr_QSLGen.html', f'config\\qsl\\{filenameQSLCard}',
                         options=imgkitOptions)
        print(f'Sending QSL card email to {q[2]}.')
        emailName = q[10].title()
        # Outlook needs to be opened by the user before QSLGen gets here.
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
        attachment = f'config\\qsl\\{filenameQSLCard}'
        mail.Attachments.Add(attachment)
        mail.Send()
        print('Email sent.')
        print('Deleting QSL card.')
        os.remove(f'config\\qsl\\{filenameQSLCard}')
        api_write.write_data(q, apiKey)
        generatedQSLs += 1
    return generatedQSLs


def generator_main(qsos, apiKey):
    generatedQSLs = 0
    yesno = ask_to_generate()
    if yesno == 'y' or yesno == 'yes' or yesno == '':
        generatedQSLs = generateQSLs(qsos, apiKey)

    elif yesno == 'n' or yesno == 'no':
        print('You have declined to send the QSLs listed above.\n')
    return generatedQSLs
