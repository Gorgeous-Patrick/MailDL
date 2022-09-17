import imaplib
import email
from email.header import decode_header
import os
import json 

home = os.path.expanduser("~")
folderPath = os.path.join(home, ".config", "maildl")
accountPath = os.path.join(folderPath, "accounts.json")
configPath = os.path.join(folderPath, "config.json")

accounts = json.load(open(accountPath))
server = accounts['server']
addr = accounts['email']
password = accounts['password']

configs = json.load(open(configPath))
outputFilePath = configs['output']

imap = imaplib.IMAP4_SSL(server)  # establish connection
 
imap.login(addr, password)  # login
 
#print(imap.list())  # print various inboxes
status, messages = imap.select("INBOX", readonly=True)  # select inbox
status, unseen = imap.search(None, "UNSEEN")
unseen = unseen[0].split()
unseen = [int(i) for i in unseen]
unseen.reverse()
 
numOfMessages = int(messages[0]) # get number of messages
 
 
def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)
 
def obtain_header(msg):
    # decode the email subject
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding)
 
    # decode email sender
    From, encoding = decode_header(msg.get("From"))[0]
    if isinstance(From, bytes):
        From = From.decode(encoding)
 
    return subject, From
 
def download_attachment(part):
    # download attachment
    filename = part.get_filename()
 
    if filename:
        folder_name = clean(subject)
        if not os.path.isdir(folder_name):
            # make a folder for this email (named after the subject)
            os.mkdir(folder_name)
            filepath = os.path.join(folder_name, filename)
            # download attachment and save it
            open(filepath, "wb").write(part.get_payload(decode=True))
 
 

with open(outputFilePath, "w") as f:
    print("Total number of unread emails: ", len(unseen), file = f)
    for i in unseen:
        res, msg = imap.fetch(str(i), "(RFC822)")  # fetches the email using it's ID
     
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
     
                subject, From = obtain_header(msg)
                print("=" * 50, file = f)
                print(f"Subject: {subject}\nFrom: {From}", file = f)
     
imap.close()
