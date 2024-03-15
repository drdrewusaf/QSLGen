# QSLGen
QSLGen is a utility for Ham Radio operators to generate QSL cards, email them (using the MS Outlook client with a properly setup email account) to station operators with public email addresses on QRZ.com, and update eQSL Sent info for each emailed QSL card on QRZ.com.

> [!NOTE]
> You must be at least an XML subscription holder at QRZ.com to use your API key(s) in QSLGen.

> [!IMPORTANT]
> QSLGen requires the following applications/packages either as part of the Python environment, or on the PC.  Please install them properly before trying to run QSLGen.
> <table>
> <tr>
> <th>Python Environment</th>
> <th>Applications</th>
> </tr>
> <tr>
> <td>
> <table>
> <tr><td><a href="https://pypi.org/project/beautifulsoup4/">Beautiful Soup 4</a></td></tr>
> <tr><td><a href="https://pypi.org/project/html2text/">html2text</a></td></tr>
> <tr><td><a href="https://pypi.org/project/adif-io/">adif_io</a></td></tr>
> <tr><td><a href="https://pypi.org/project/imgkit/">imgkit</a></td></tr>
> <tr><td><a href="https://pypi.org/project/pywin32/">pywin32</a></td></tr>
> </table>
> </td>
> <td>
> <table>
> <tr><td><a href="https://microsoft.com">MS Outlook Client</a></td></tr>
> <tr><td><a href="https://wkhtmltopdf.org">wkhtmltoimage**</a></td></tr>
> </table>
> </td>
> </tr> </table>
> **You <strong>MUST</strong> add wkhtmltoimage's install directory to your system PATH for the script to run.  Here are some OK instructions to help you along...<a href="https://www.wikihow.com/Change-the-PATH-Environment-Variable-on-Windows">WikiHow Link</a>
***
## Setup
You must edit the python script, background image, and html file before running QSLGen.  Additionally, you will need to inform QSLGen of your API key(s).

### Essential Script Edits
Set the ```imgkitOptions``` and ```myName``` variables for your use case. 
```python
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
```
The ```imgkitOptions``` variable defines the size of the image as well as the format.  The dimensions should probably match your background image, but edit as you see fit for your customized HTML file.
> [!WARNING]
> As mentioned in the script, you must leave the ```enable-local-file-access``` option or imgkit will not be able to read/write your QSL Cards.

### Background Image
If you choose to have a background image the filename <strong>MUST</strong> follow the naming convention of the included file for <strong>ALL</strong> callsigns/API keys QSLGen will run through.  The naming convention is your callsign in all caps followed by underscore ( _ ) followed by "bg".  If you have a prefix or suffix on a callsign, replace the slash ( / ) with an underscore ( _ ).
- Regular callsign (ex. DA6AJP): ```DA6AJP_bg.jpg```
- Callsign with prefix (ex. SO/DA6AJP): ```SO_DA6AJP_bg.jpg```

### HTML Files
QSLGen uses two html files.
- QSLGen.html
- Curr_QSLGen.html

The QSLGen.html file ships with/is included with the QSLGen package and is where the script uses DOM selectors to create a customized QSL Card.  You can edit the file to your preference, but be aware of variables that the script may be searching to edit.

The Curr_QSLGen.html file is created on the fly while QSLGen is running and iterating through your QSOs.  It is also used as the indicator of the last time QSLGen was run.  
> [!NOTE]
> On the first run, QSLGen will ask for a starting date.  After it finishes, and as long as the Curr_QSLGen.html file is in the working directory, QSLGen will use Curr_QSLGen.html's "Date Modified" attribute to determine the starting date.


### API Key(s)
QSLGen will ask you for your API key(s) if it does not find an apikey.txt file, or finds an empty apikeys.txt file, in the working directory.  You can enter them in the program and it will create or fill the file with the API keys given.  Alternatively, you can manually create the file in the working directory.  If you have multiple API keys, they must be separated by commas with no spaces.
> [!CAUTION]
> QSLGen stores your API key(s) in plain text.  Keep the location/file secure if you're worried.
***
## Usage
Simply run the python script after fulfilling the requirements above, and follow the onscreen prompts.
```
python main.py
```
> [!IMPORTANT]
> QSLGen will update your QRZ.com QSO records by setting eQSL Sent to true with the current date.  There is not currently a mechanism to prevent it save for removing or commenting out lines 144-167:
```python
print('Updating QSO on QRZ.com to reflect eQSL sent.')
# Array position reference again: 0APP_QRZLOG_LOGID, 1BAND, 2CALL, 3EMAIL, 4EQSL_QSL_SENT,
# 5FREQ, 6MODE, 7MY_CITY, 8MY_COUNTRY, 9MY_GRIDSQUARE, 10NAME, 11QSO_DATE,
# 12RST_RCVD, 13STATION_CALLSIGN, 14TIME_ON, 15RST_SENT, 16TX_PWR, 17COMMENT, 18NOTES
payloadAdifData = payloadAdifSelector(q)
updatePayload = {'KEY': f'{ak}',
                 'ACTION': 'INSERT',
                 'OPTION': 'REPLACE',
                 'ADIF': payloadAdifData +
                 f'<eqsl_qsl_sent:1>Y'
                 f'<eqsl_qslsdate:{len(today)}>{today}'
                 f'<eor>'}

url = 'https://logbook.qrz.com/api'
insertResponse = requests.get(url, params=updatePayload)
if 'REPLACE' not in insertResponse.text:
    with open('log.txt', 'a') as log:
        logWriter(f'QRZ.com reported an error while updating the QSO'
                  f' with callsign {q[2]}.\n'
                  f'Here is the response:  {insertResponse.text}\n',
                  end=True)
        print(f'QRZ.com reported an error: {insertResponse.text}')
else:
    print('QRZ.com QSO updated.')
```
