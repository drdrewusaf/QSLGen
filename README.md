# QSLGen <img src="https://github.com/drdrewusaf/QSLGen/blob/master/images/QSL%20Icon.png" alt="Icon" width="150"/>
QSLGen is a utility for Ham Radio operators to generate QSL cards for station operators with public email addresses on QRZ.com and email them via Gmail OAuth API or save them locally for use in any email client. It can also update eQSL Sent info for each emailed QSL card on QRZ.com.

> [!NOTE]
> You must be at least an XML subscription holder at QRZ.com to use your API key(s) in QSLGen.

> [!IMPORTANT]
> QSLGen requires the following packages in the Python environment. Please install them properly before trying to run QSLGen.
> <table>
> <tr><td><a href="https://pypi.org/project/beautifulsoup4/">Beautiful Soup 4</a></td>
> <td><a href="https://pypi.org/project/html2image/">html2image</a></td>
> <td><a href="https://pypi.org/project/html2text/">html2text</a></td></tr>
> <tr><td><a href="https://pypi.org/project/adif-io/">adif_io</a></td>
> <td><a href="https://pypi.org/project/cryptography/">cryptography</a></td>
> <td><a href="https://pypi.org/project/google-auth-oauthlib/">google-auth-oauthlib</a></td></tr>
> <tr><td><a href="https://pypi.org/project/google-api-python-client/">google-api-python-client</a></td>
> <td><a href="https://pypi.org/project/api-client/">apiclient</a></td>
> <td><a href="https://pypi.org/project/requests/">requests</a></td></tr>
> </table>
***
### Setup
Please go into the settings menu when you first launch QSLGen.

#### Gmail Setup
If you wish to use the Gmail API, you need to setup OAuth for your account and download the OAuth Client Secrets JSON file. You will be able to copy and paste the contents into QSLGen at runtime. QSLGen will encrypt the json data and save it for future use.

> [!IMPORTANT]
> You do NOT need to, but you can choose to publish and verify the app in your cloud console whenever you desire. The instructions below only take you as far as setting up your OAuth Client in testing status (which is perfectly fine for personal use).

To setup your API:
#### 1. Create a Google Cloud Project 
- Go to the Google Cloud Console 
- Create a new project or select an existing one. 
- Navigate to APIs & Services > Library and search for "Gmail API." 
- Select the Gmail API and click Enable.

#### 2. Configure the OAuth Consent Screen
- Go to APIs & Services > OAuth consent screen. 
- Select User Type:  External
- Fill in the required App Information (App name, user support email, and developer contact info). 
- Add the Send Email Scope (Search for Gmail API scopes). 
- Add Test Users: While in "Testing" status, only added test users can authorize the app.

#### 3. Create OAuth 2.0 Credentials 
- Go to APIs & Services > Credentials. 
- Click Create Credentials and select OAuth client ID. 
- Select the Application type: Desktop app 
- Click Create to receive your Client ID and Client Secret. 
- Download the JSON file containing these credentials for use in your application.

### Background Image
If you choose to have a background image the filename <strong>MUST</strong> follow the naming convention of the included file for <strong>ALL</strong> callsigns/API keys QSLGen will run through.  The naming convention is your callsign in all caps followed by underscore ( _ ) followed by "bg".  If you have a prefix or suffix on a callsign, replace the slash ( / ) with an underscore ( _ ).
- Regular callsign (ex. DA6AJP): ```DA6AJP_bg.jpg```
- Callsign with prefix (ex. SO/DA6AJP): ```SO_DA6AJP_bg.jpg```

### HTML Files
QSLGen uses two html files.
- QSLGen.html
- Curr_QSLGen.html

The QSLGen.html file ships with/is included with the QSLGen package and is where the script uses DOM selectors to create a customized QSL Card.  You can edit the file to your preference, but be aware of variables that the script may be searching to edit.

The Curr_QSLGen.html file is created on the fly while QSLGen is running and iterating through your QSOs.  

### API Key(s)
QSLGen needs your API key(s). You can enter them in the program, and it will create and encrypt an apikeys.txt file with the API keys given.

***
## Usage
Simply run the python script after fulfilling the requirements above, and follow the onscreen prompts.
```
python main.py
```
