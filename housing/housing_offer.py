import sys
import os
import smtplib
import subprocess
import numpy as np
from warnings import warn
from tempfile import TemporaryDirectory
from email.message import EmailMessage
import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from astropy.table import Table
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mimetypes
import base64
import pandas as pd

from os.path import expanduser
home = expanduser("~")
sys.path.append(home + '/repos/cs22website/pagepy')
from housing import process_spreadsheet_value


def send_message(service, user_id, message):
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    print('Message Id: %s' % message['id'])
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None


def set_timestamp(sheet, col, row, status=''):
    '''Put timestamp into a specific cell in a Google sheet.

    The timestamp is written in the same string format that Google uses
    by default to mark the time a Google from entry was written.

    Parameters
    ----------
    sheet : gspread worksheet
    col : int
        column number (0 based as in Python)
    row : int
        row number (0 based as in Python)
    status : string
        A prefix to the time stamp. This can be used to
        mark a cell that is currently processed.
    '''
    val = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    sheet.loc[row-1, 'confemail'] = val
    #sheet.update_cell(row + 1, col + 1, status + val)


def send_conf_email(dat):
    if len(dat) != 1:
        raise ValueError('Table with data for email needs to have exactly one row.')
    with open(home + '/gmail.txt') as f:
        password = f.read()
    password = password[:-1]
    process_spreadsheet_value(dat)

    # Create the container email message.
    msg            = EmailMessage()
    msg['From']    = 'coolstars22sd@gmail.com'
    msg['To']      = dat['Email Address']
    msg['Subject'] = 'CS22 Housing details'
    emailtext      = env.get_template('housing_email.txt')
    msg.set_content(emailtext.render(dat=dat[0]))
    print(emailtext.render(dat=dat[0]))

    raw_message  = base64.urlsafe_b64encode(msg.as_string().encode("utf-8"))
    full_message = {'raw': raw_message.decode("utf-8")}

    #print(full_message)

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

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
            flow = InstalledAppFlow.from_client_secrets_file(
              home + "/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(home + "/token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    send_message(service=service, user_id='Me', message=full_message)

    print('{}: Send email to: {}'.format(datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                                             msg['To']))


env = Environment(loader=FileSystemLoader([home+'/repos/cs22website/templates']),
                  autoescape=select_autoescape(['html']))

parse_sheet_timestamp = re.compile("(?P<year>[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+)T(?P<hour>[0-9]+):(?P<minute>[0-9]+):(?P<second>[0-9]+)")

"""
# pip install --upgrade google-auth-oauthlib
# use creds to create a client to interact with the Google Drive API
scope  = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds  = ServiceAccountCredentials.from_json_keyfile_name('../../../CS22Gkey.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Cool Stars 22 Abstract Submission (Responses)").sheet1
"""
df    = pd.read_excel(home + '/Downloads/Cool Stars 22 Housing Tracker_Upload Info_test.xlsx')
#print(df)
#gc    = gspread.service_account()
sheet = df#gc.open("Cool Stars 22 Abstract Submission (Responses)").sheet1

#list_of_lists = df.get_all_values()
#g_sheet = Table(rows=list_of_lists[1:], names=list_of_lists[0])
g_sheet = Table.from_pandas(df)

print(g_sheet)
#print(g_sheet.colnames)
#print(g_sheet.colnames == 'confemail')
#print(np.where(g_sheet.colnames == 'confemail'))
#print(df.columns.get_loc('confemail'))
ind_conf = df.columns.get_loc('confemail')
#print(ind_conf)

for i, ts in enumerate(g_sheet['Timestamp']):
    print(i, ts)
    match = parse_sheet_timestamp.match(str(ts))
    print(match)
    # The following loop is not written in the most concise way,
    # but is a way that makes it easy to follow the logic
    if match != None:
        print('1111')
        #print(ind_conf[i], type(ind_conf[i]), ind_conf[i] == '')
        # New entry. No conf email send yet or timestamp removed
        # by hand in sheet to trigger resending
        if g_sheet['confemail'][i].astype(str).filled(fill_value='') == '':
            # check if they paid
            #print(g_sheet['Date Payment Received'][i])
            if g_sheet['Date Payment Received'][i] != '':
                print('2222')
                set_timestamp(sheet, ind_conf, i + 1, status='Working on ')
                print(sheet)
                #sys.exit()
                send_conf_email(g_sheet[[i]])
                set_timestamp(sheet, ind_conf, i + 1)
                #sys.exit()
        else:
            #sys.exit()
            matchconf = parse_sheet_timestamp.match(g_sheet['confemail'][i])
            if matchconf is None:
                warn('Cannot parse time for confemail: {}'.format(g_sheet['confemail'][i]))
            else:
                # entry has been modified
                if (datetime(**{k: int(v) for k, v in match.groupdict().items()}) >
                   datetime(**{k: int(v) for k, v in matchconf.groupdict().items()})):
                    set_timestamp(sheet, ind_conf, i + 1, status='Working on ')
                    send_conf_email(g_sheet[[i]])
                    set_timestamp(sheet, ind_conf, i + 1)

print('Done processing')
