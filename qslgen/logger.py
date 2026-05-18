"""
Log writer...
"""
from qslgen import today


def writer(message, end=True):
    with open('log.txt', 'a') as log:
        log.write(f'{message}\n')
        if end:
            log.write(f'End of log on {today}\n'
                      f'*********************************\n')
        log.close()
