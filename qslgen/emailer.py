"""
Builds an email and either saves it locally, or sends it via Gmail OAuth API.
"""
import base64
import mimetypes
from email.message import EmailMessage
from pathlib import Path

from apiclient import errors


def send_email(service, msg):
    """
    Send the QSL email via Gmail OAuth API
    :param service: the Gmail OAuth service
    :param msg: url-safe, base64-encoded email to be sent
    """
    try:
        message = (service.users().messages().send(userId='me', body=msg).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"


def generate_email(sendOrSave, todayDir, qslCard, filename, myName, q, service):
    """
    Generate an email file or encoded message and save it or send it.
    :param sendOrSave: user setting to send the email via Gmail OAuth API or save locally as .eml file
    :param todayDir: directory for today's session
    :param qslCard: QLS card image file
    :param filename: filename for the .eml file
    :param myName: user setting for their name in the email signature
    :param q: dict of the qso being worked
    :param service: Gmail OAuth service or null
    """
    emailName = q[10].title()
    to = f'{q[3]}'
    subject = f'QSL de {q[13]}'
    body = (f'Good Day {emailName} ({q[2]})!\n\n'
            f'Thank you for the QSO!  You will find my QSL card attached.  '
            f'Hope to hear you on the air again soon!\n\n\n'
            f'73,\n'
            f'{q[13]}\n'
            f'{myName}\n\n'
            f'* This email was automatically generated and sent using the QSLGen Python script '
            f'by KF3OFP/DA6AJP: https://github.com/drdrewusaf/QSLGen *')
    message = EmailMessage()
    message['to'] = to
    message['subject'] = subject
    message.set_content(body)
    contentType = mimetypes.guess_type(qslCard)
    mainType, subType = contentType[0].split('/')
    with open(qslCard, 'rb') as att:
        qslCardData = att.read()
        att.close()
    message.add_attachment(qslCardData, mainType, subType)

    if sendOrSave == 'SEND':
        print(f'Sending QSL card email to {q[2]}.')
        encodedMessage = base64.urlsafe_b64encode(message.as_bytes()).decode()
        msg = {"raw": encodedMessage}
        send_email(service, msg)
    else:
        emlFile = Path.joinpath(todayDir, f'{filename}.eml')
        with open(emlFile, 'wb') as eml:
            eml.write(message.as_bytes())
        print(f'Message saved as {emlFile}')
