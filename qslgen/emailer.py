import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors
import mimetypes
from email.mime.image import MIMEImage


def send_email(service, msg):
    try:
        message = (service.users().messages().send(userId='me', body=msg).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"


def generate_email(sendOrSave, todayDir, filename, myName, q, service):
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
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    content_type, encoding = mimetypes.guess_type(f'{todayDir}\\{filename}.jpg')
    main_type, sub_type = content_type.split('/', 1)
    qsl_card = open(f'{todayDir}\\{filename}.jpg', 'rb')
    attachment = MIMEImage(qsl_card.read(), _subtype=sub_type)
    qsl_card.close()
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(attachment)

    encodedMessage = {'raw': base64.urlsafe_b64encode(message.as_string())}

    if sendOrSave == 'SEND':
        print(f'Sending QSL card email to {q[2]}.')
        send_email(service, encodedMessage)
    else:
        with open(f'{todayDir}\\{filename}.eml', 'wb') as eml:
            eml.write(message.as_bytes())
        print(f'Message saved as {todayDir}\\{filename}.eml')
