import datetime
from pathlib import Path

__package_name__ = 'QSLGen'
__version__ = 1.6
__author__ = 'KF3OFP'

# These are the dictionary keys in the ADIF data we want to work with.
wantedAdifKeys = ['APP_QRZLOG_LOGID', 'BAND', 'CALL', 'EMAIL', 'EQSL_QSL_SENT',
                  'FREQ', 'MODE', 'MY_CITY', 'MY_COUNTRY', 'MY_GRIDSQUARE', 'NAME',
                  'QSO_DATE', 'RST_RCVD', 'STATION_CALLSIGN', 'TIME_ON', 'RST_SENT', 'TX_PWR',
                  'COMMENT', 'NOTES', 'APP_QRZLOG_QSLDATE', 'LOTW_QSLRDATE']

# User agent header requirement per QRZ.com API specification
headers = {'User-Agent': f'{__package_name__}/{__version__} ({__author__})'}

today = str(datetime.date.today())

userDir = Path.joinpath(Path.home(), 'QSLGen')
configDir = Path.joinpath(Path(__file__).parent, 'config')
qslFilesDir = Path.joinpath(configDir, 'qsl')
cryptoKeyFile = Path.joinpath(userDir, 'key.key')
settingsFile = Path.joinpath(configDir, 'settings.json')
apiKeysFile = Path.joinpath(configDir, 'apikeys.txt')
oauthFile = Path.joinpath(configDir, 'oauth.json')
