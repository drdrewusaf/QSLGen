import datetime
from qslgen import wantedAdifKeys

reduced_qsos = []


def underscore_check(ixCall):
    """
    QRZ.com returns prefixed and suffixed callsigns with an underscore.
    This function returns it to a slash for the QSL card and email text, and
    returns it to an underscore for filenames.
    """
    if '_' in ixCall:
        ixCall = ixCall.replace('_', '/')
    elif '/' in ixCall:
        ixCall = ixCall.replace('/', '_')
    return ixCall


def adif_key_selector_formatter(qsos):
    """
    Search for and keep desired ADIF keys and format callsigns with a slash for emailing.
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
    selected_qsos = adif_key_selector_formatter(qsos)
    qsoCount = 0
    while qsoCount < len(selected_qsos):
        """ 
        Find out if QSOs are modified after their QSL date and their QSL date is older than dateSince.
        This is kind of janky - QRZ seems to update their QSL date whenever the QSO is updated.
        So, we're trying to use LOTW_QSLRDATE, if it's there, as a sanity check first.
        """
        qslDate = datetime.date.fromisoformat(selected_qsos[qsoCount][19])
        if len(selected_qsos[qsoCount][20]) > 0:
            lotwQslRDate = datetime.date.fromisoformat(selected_qsos[qsoCount][20])
            if lotwQslRDate < qslDate:
                qslDate = lotwQslRDate
        # Remove QSOs that have already been eQSL'd, do not have a public email, or are older than dateSince
        if len(selected_qsos[qsoCount][3]) <= 0 or 'Y' in selected_qsos[qsoCount][4]:
            del selected_qsos[qsoCount]
        elif qslDate < dateSince:
            del selected_qsos[qsoCount]
        else:
            qsoCount += 1
    return selected_qsos
