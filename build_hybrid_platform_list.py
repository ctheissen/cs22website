import pandas as pd
import os.path, sys
import numpy as np
'''
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1H-Z5tkws92Idw6tNdU9dLhpdAOkEqz3sryfmbYErsNU"
SAMPLE_RANGE_NAME = "Class Data!A2:E"

from os.path import expanduser
home = expanduser("~")

creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
if os.path.exists(home + "/token.json"):
    creds = Credentials.from_authorized_user_file(home + "/token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        print('YES')
        flow = InstalledAppFlow.from_client_secrets_file(
            home + "/credentials.json", SCOPES
            )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
        print("No data found.")

    print("Name, Major:")
    for row in values:
        # Print columns A and E, which correspond to indices 0 and 4.
        print(f"{row[0]}, {row[4]}")
except HttpError as err:
    print(err)




print(sheet)
sys.exit()
'''
df1 = pd.read_excel('/Users/ctheissen/Google Drive/CS22_Planning_Documents/Registration/Reports/Registrant Details_Full_6.6.xlsx')
print(df1)
firstname = []
lastname = []
for name in df1['Full Name'].values:
    firstname.append(name.split(',')[1].strip(' '))
    lastname.append(name.split(',')[0])

'''
print(pd1['Email Address'])
print('woodml@mit.edu' in pd1.values)
print('anna_zuckerman@alumni.brown.edu' in pd1)
print('anna_zuckerman@alumni.brown.edu' in pd1['Email Address'].values)
print(pd1['Email Address'].iloc[-1])
print('anna_zuckerman@alumni.brown.edu' == pd1['Email Address'].iloc[-1])
sys.exit()
'''
#abstracts = pd.read_excel('/Users/ctheissen/Downloads/Cool Stars 22 Abstract Submission (Responses).xlsx')
xls = pd.ExcelFile('/Users/ctheissen/Downloads/Cool Stars 22 Abstract Submission (Responses).xlsx')
abstracts = pd.read_excel(xls, 'Final')
#abstracts = pd.read_excel('/Users/ctheissen/Downloads/Cool Stars 22 Abstract Submission (Responses).xlsx')
print(abstracts)
absAuthors = []
for name in abstracts['Authors'].values:
    if ',' in name: namelist = name.split(',')
    elif ';' in name: namelist = name.split(';')
    else: namelist = name
    absAuthors.append(namelist)
print(absAuthors)
print("Schröder" in absAuthors)
count = 0
for namet in absAuthors: 
    count += 1
    #print(namet)
    counts2 = []
    count2  = 0
    for namet2 in namet:
        if "Schröder" in namet2: 
            counts2.append(count2)
            print(count, count2, namet, namet2)
        count2+=1
sys.exit()
df2 = pd.read_excel('/Users/ctheissen/Downloads/Cool Stars 22 Poster Submissions (Responses).xlsx')
print(df2)

C = pd.merge(df2,abstracts,how='left',left_on='Email Address',right_on='Email Address')#.drop(['Email Address'], axis=1)
print(C)

# iterating the columns
for col in C.columns:
    print(col)

titles  = []
nameArr = []
emails  = []
abstractArr = []

for i in range(len(df2)):
    #print(i)
    # First check that they are registered for the conference and do not have an outstanding balance.
    #print(C.iloc[i])
    email1 = C['Email Address'][i]
    print(i, email1)
    name1 = C['Presenting Author Name'][i]
    if email1 == 'vidakris@gmail.com': continue
    #print(email1 not in pd1['Email Address'].values)
    if email1 not in df1['Email Address'].values: 
        # Do a deeper dive
        #print('%s EMAIL NOT REGISTERED'%email1)
        #print(name1)
        if ',' not in name1:
            name12 = name1.split(' ')
            testname = name12[-1]
        else:
            name12 = name1.split(',')
            testname = name12[0]
        #print(name12, testname)
        if testname in lastname:
            print('%s NAME NOT REGISTERED'%name1)
            break

    # They are registered
    # Now we X-match to the abstracts
    j = np.where(abstracts['Email Address'].values == email1)[0]
    print(j)
    print(len(j))
    # If there is only one match this is good!
    if len(j) == 1: 
        index1 = j[0]
    if len(j) == 0: 
        print('NO MATCHES!')
        # Need to search by name
        #print(name1)
        if ',' not in name1:
            name12 = name1.split(' ')
            testname = name12[-1]
        else:
            name12 = name1.split(',')
            testname = name12[0]
        print(name12, testname)
        if testname not in absAuthors:
            print('%s NAME NOT REGISTERED'%name1)
            break





        break
    if len(j) > 1: 
        print('TOO MANY MATCHES!')
        for k in j: 
            print(k)
            print(abstracts.iloc[k])
        break
    print('Index', index1)
    #sys.exit()

    title  = abstracts['Title'].iloc[index1]
    names  = abstracts['Authors'].iloc[index1]
    print(title)
    print(names)
    #print(C['Abstract'][i])
    abstract_text  = abstracts['Abstract'].iloc[index1].replace('\n', ' ').replace('\r', '')
    theme  = abstracts['Select a major science topic'].iloc[index1]
    abstract_url = ''
    presentation_date,presentation_time = '',''
    poster_pdf_url = df2['Please upload your PDF poster here.'].iloc[i]
    thumbnail_url, poster_url, zenodo_url, optional_url = '','','',''

    #print(name1)
    #email2 = abstracts["Email Address"]==email1
    #print(name2)
    print(title, names, email1, abstract_url, abstract_text, theme, presentation_date, presentation_time, poster_pdf_url, thumbnail_url, poster_url, zenodo_url, optional_url)
    titles.append(title)
    nameArr.append(names)
    emails.append(email1)
    abstractArr.append(abstract_text)

sys.exit()
total = len(pd1)
print(total)

# above_35 = titanic[titanic["Age"] > 35]

totalin  = len(pd[pd["Registration Type"]=="Conference Attendee"])
totalvir = len(pd[pd["Registration Type"]=="Conference Attendee - Virtual"])
print(totalin)

print("<p>%s participants are currently registered (%s in-person, %s remotely):</p>"%(total, totalin, totalvir))
print()
print('<ul class="listing">')
print()
lastname = ''
for i in range(len(pd)):

    #print(pd['Full Name'][i], pd['Company Name'][i], pd['Amount Due'][i], pd['Amount Paid'][i], pd['Amount Ordered'][i])
    #print(pd['Amount Paid'][i] == 0) 
    #print((pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800))
    #print((pd['Amount Ordered'][i] < 800 and pd['Amount Due'][i] >= 540))
    #print((pd['Amount Paid'][i] == 0 and pd['Amount Due'][i] != 0) or (pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800))
    #print((pd['Amount Ordered'][i] < 800 and pd['Amount Due'][i] >= 540))
    #if (pd['Amount Due'][i] != 0) or (pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800): continue
    if (pd['Amount Paid'][i] == 0 and pd['Amount Due'][i] != 0) or (pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800): continue
    if (pd['Amount Ordered'][i] < 800 and pd['Amount Due'][i] >= 540): continue
    name        = pd['Full Name'][i]
    #print(name)
    institution = pd['Company Name'][i]
    if pd['Registration Type'][i] == "Conference Attendee - Virtual": type1 = "virtual"
    elif pd['Registration Type'][i] == "Conference Attendee": type1 = "in-person"
    if name == lastname:
        print('SAME NAME')
        break
    lastname = name

    print('<li><span style="color: #00629B;"> %s </span> - %s [%s]</li>'%(name, institution, type1))
    print()
    #break