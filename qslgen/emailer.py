import base64
import mimetypes
from pathlib import Path
from email.message import EmailMessage

from apiclient import errors


def send_email(service, msg):
    try:
        message = (service.users().messages().send(userId='me', body=msg).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"


def generate_email(sendOrSave, todayDir, qslCard, filename, myName, q, service):
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
    encodedMessage = base64.urlsafe_b64encode(message.as_bytes()).decode()
    msg = {"raw": encodedMessage}

    send_email(service, msg)

    if sendOrSave == 'SEND':
        print(f'Sending QSL card email to {q[2]}.')
        send_email(service, encodedMessage)
    else:
        emlFile = Path.joinpath(todayDir, f'{filename}.eml')
        with open(emlFile, 'wb') as eml:
            eml.write(message.as_bytes())
        print(f'Message saved as {emlFile}')
