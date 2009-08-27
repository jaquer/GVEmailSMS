#!/usr/bin/env python

__appname__ = 'GVIMAPSMS'
__version__ = '0.1'

# Constants
CFG_FILE = 'settings.cfg'
PWD_FILE = 'passwords.cfg'

import re, sys, time
from email.parser import Parser
from email.utils import parseaddr

import googlevoice
import imaplib2

from modules import config, smtp

def main():

    cfg = config.Config(CFG_FILE, PWD_FILE)

    for section in 'google', 'smtp', 'imap':
        cfg.read_password(section)

    mailer = smtp.Mailer(cfg)

    g = cfg['google']
    gv = googlevoice.Voice()
    gv.login(g['username'], g['password'])

    i = cfg['imap']
    if i['ssl']:
        imap = imaplib2.IMAP4_SSL(i['server'], i['port'])
    else:
        imap = imaplib2.IMAP(i['server'], i['port'])

    # Variable to hold ids of messages currently in Inbox
    replies = []

    # SEARCH command to use when looking for emails
    SEARCH_CMD = '(UNSEEN FROM "' + cfg['main']['notify'] + '")'

    # Incoming email regular expressions
    e = cfg['email']
    EMAIL_REGEX   = re.escape(e['username'] + '+') + r'(\d{10})' + re.escape('@' + e['domain'])
    EMAIL_REGEX   = re.compile(EMAIL_REGEX, re.IGNORECASE)
    SUBJECT_REGEX = re.compile(r'(\d{10})')

    imap.login(i['username'], i['password'])
    imap.select()

    # Build list of current messages
    tmp, data = imap.search(None, SEARCH_CMD)

    for num in data[0].split():
        replies.append(num)
        
    print 'Starting loop.'

    while True:

        # IDLE blocks until new email arrives, or it times out
        imap.idle(15 * 60)

        tmp, data = imap.search(None, SEARCH_CMD)

        for num in data[0].split():

            if not num in replies:

                print 'New email message received.'

                tmp, data = imap.fetch(num, '(RFC822)')
                msg = data[0][1]

                incoming = Parser().parsestr(msg, True)

                # Extract phone number to send SMS to
                subject = incoming['Subject']
                
                match = SUBJECT_REGEX.search(subject)
                
                if not match:
                
                    # Try one more time, this time searching "To" header.
                    to = incoming['To']
                    name, addr = parseaddr(to)

                    match = EMAIL_REGEX.search(addr)

                    if not match:
                        # Invalid email address format
                        subject = 'Invalid Phone Number'

                        print '  %s.' % subject
                        
                        body = 'The phone number you specified in the email you sent is invalid.\n\n'
                        body += 'Phone number must be 10 digits (area code + phone number). Please try again.\n'

                        mailer.send_email(subject, body)
                        
                        imap.store(num, 'FLAGS', '(\Seen \Deleted)')
                        #imap.expunge()
                    
                number = match.group(1)

                for part in incoming.walk():
                    if part.get_content_type() == 'text/plain':
                        message = part.get_payload().splitlines()[0]

                imap.store(num, 'FLAGS', '(\Seen \Deleted)')
                #imap.expunge()

                gv.send_sms(number, message)

                print '  Message fowarded to %s.' % number
                
            
    # FIXME: This never happens. Need a try/except block somewhere.
    imap.close()
    imap.logout()
    
    
if __name__ == '__main__':

    while True:
        try:
            print '%s v%s - Starting up.' % (__appname__, __version__)
            main()
        except KeyboardInterrupt:
            print 'Process cancelled. Exiting.'
            time.sleep(2)
            sys.exit(0)
        except:
            print 'Unexpected error. Exiting.'
            raise
