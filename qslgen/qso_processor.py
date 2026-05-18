"""
Process QSOs retrieved from QRZ.
"""
import datetime

from qslgen import wantedAdifKeys

reduced_qsos = []


def underscore_check(ixCall):
    """
    QRZ.com uses an underscore with prefixed and suffixed callsigns. This function will either
    replace the underscore with a slash to make the QSL card and email prettier, or the opposite for
    writing the QSL card files.
    """
    if '_' in ixCall:
        ixCall = ixCall.replace('_', '/')
    elif '/' in ixCall:
        ixCall = ixCall.replace('/', '_')
    return ixCall


def adif_key_selector_formatter(qsos):
    """
    Search for and keep desired ADIF keys and format callsigns with a slash for emailing.
    :param qsos: the dict of QSOs received from QRZ for the associated API key with ALL the ADIF data
    :return reduced_qsos: the dict of QSOs with on ADIF data we need/use
    """
    for q in qsos:
        reduced_qsos = []
        curr_qso = []
        keyCount = 0
        while keyCount < len(wantedAdifKeys):
            if wantedAdifKeys[keyCount] not in q.keys():
                curr_qso.append('')
                keyCount += 1
            else:
                if keyCount == 2:
                    callDistantSlash = underscore_check(q[wantedAdifKeys[keyCount]])
                    curr_qso.append(callDistantSlash)
                elif keyCount == 13:
                    callLocalSlash = underscore_check(q[wantedAdifKeys[keyCount]])
                    curr_qso.append(callLocalSlash)
                else:
                    curr_qso.append(q[wantedAdifKeys[keyCount]])
                keyCount += 1
        reduced_qsos.append(curr_qso)
    return reduced_qsos


def processor(qsos, dateSince):
    """
    Process the list of QSOs from QRZ. Remove QSOs that are already eQSL'd or do not have a public email address,
    without which we cannot send a QSL card. Then, select only the ADIF data the author deemed pertinent.
    :param qsos: the entire list of QSOs received from QRZ meeting API key and date since criteria
    :param dateSince: date from which we request QSOs from QRZ - used for sanity check with LOTW-updated QSOs
    :return selected_qsos: a reduced list of QSOs that are not eQSL'd and contain data the author deemed pertinent
    """
    qsoCount = 0
    while qsoCount < len(qsos):
        """ 
        Find out if QSOs are modified after their QSL date and their QSL date is older than dateSince.
        This is kind of janky - QRZ seems to update their QSL date whenever the QSO is updated.
        So, we're trying to use LOTW_QSLRDATE, if it's there, as a sanity check first.
        """
        qslDate = datetime.date.fromisoformat(qsos[qsoCount][19])
        if len(qsos[qsoCount][20]) > 0:
            lotwQslRDate = datetime.date.fromisoformat(qsos[qsoCount][20])
            if lotwQslRDate < qslDate:
                qslDate = lotwQslRDate
        # Remove QSOs that have already been eQSL'd, do not have a public email, or are older than dateSince
        if len(qsos[qsoCount][3]) <= 0 or 'Y' in qsos[qsoCount][4]:
            del qsos[qsoCount]
        elif qslDate < dateSince:
            del qsos[qsoCount]
        else:
            qsoCount += 1
    selected_qsos = adif_key_selector_formatter(qsos)
    return selected_qsos
