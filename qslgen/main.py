import datetime
import os
import re
import qso_processor
import qsl_generator
import menu as menu
import qrz_api.read as api_read
from logger import writer as log_writer


def define_datesince():
    """
    Check if there is a previously generated html file and base our dateSince variable on it.
    Otherwise, ask the user for a date.
    """
    try:
        dateSince = datetime.date.fromtimestamp(os.path.getmtime('config\\qsl\\Curr_QSLGen.html'))
    except FileNotFoundError:
        needDate = True
        while needDate:
            print('\nCould not find Curr_QSLGen.html file. Assuming this is the first run.\n'
                  'This program uses the last modified date of the Curr_QSLGen.html file to\n'
                  'determine which QSOs to download. Since that file does not exist, please \n'
                  'provide the first date from which to gather confirmed QSOs. After this\n'
                  'first run, the Curr_QSLGen.html file should not be deleted or modified by\n'
                  'anything other than this script. As long as the file exists, you will not\n'
                  'be asked for a date again. Suggest using a relatively recent date.\n')
            dateSince = input('\nPlease provide your desired date in the YYYY-MM-DD format:  ')
            if re.match('^(\\d){4}-(\\d){2}-(\\d){2}', dateSince):
                dateSince = datetime.date.fromisoformat(dateSince)
                needDate = False
            else:
                print('Invalid format.')
    return dateSince


def main():
    totalGeneratedQSLs = 0
    dateSince = define_datesince()
    opt, apiKeys = menu.main_menu()
    apiKeyCount = 0
    if opt == 'q':
        exit(0)
    elif opt == 'g':
        for ak in apiKeys:
            qso_data = api_read.request_data(ak, dateSince)
            if len(qso_data) > 0:
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
            print(f'\nReady to generate and email QSL cards for {selected_qsos_len} QSOs.\n'
                  f'Here is a list of callsigns we will QSL:')
            qsoCount = 0
            for q in selected_qsos:
                if qsoCount == selected_qsos - 1:
                    print(f'{q[2]}')
                else:
                    print(f'{q[2]}, ', end='')
                    qsoCount += 1
            totalGeneratedQSLs = totalGeneratedQSLs + qsl_generator.generator_main(selected_qsos, ak)
            apiKeyCount += 1
            if len(apiKeys) - 1 < apiKeyCount:
                print(f'Moving on to next API key.')
    print(f'\nQSLGen finished sending and updating {totalGeneratedQSLs} QSLs for confirmed QSOs since {dateSince} '
          f'using the provided API keys.\n')
    if totalGeneratedQSLs > 0:
        print(f'You should check your email sent items and QRZ.com to ensure everything processed as expected.\n\n')
    input(f'Press Enter to exit.')
    # End the log entries
    log_writer('', end=True)
    exit(0)


if __name__ == "__main__":
    main()
