#!/usr/bin/env python

__appname__ = 'GVEmailSMS'
__version__ = '0.1'

# Constants
CFG_FILE = 'settings.cfg'
PWD_FILE = 'passwords.cfg'

import re, sys
from email.parser import Parser
from email.utils import parseaddr

import googlevoice

from modules import config

cfg = config.Config(CFG_FILE, PWD_FILE)

for section in 'google', 'smtp':
    cfg.read_password(section)

g = cfg['google']
gv = googlevoice.Voice()
gv.login(g['username'], g['password'])

# Incoming email regular expression
e = cfg['email']
EMAIL_REGEX = re.escape(e['username'] + '+') + r'(\d{10})' + re.escape('@' + e['domain'])
EMAIL_REGEX = re.compile(EMAIL_REGEX, re.IGNORECASE)

incoming = Parser().parse(sys.stdin, True)

frm = incoming['From']
name, addr = parseaddr(frm)

if addr.lower() != cfg['main']['notify'].lower():
    # Received a message from unrecognized email
    from modules import smtp
    
    mailer = smtp.Mailer(cfg)
    
    subject = 'Unauthorized Usage'
   
    body = 'An email has been received from unauthorized email address: <%s>\n\n' % addr
    body += 'Complete original email follows:\n\n'
    body += incoming.as_string(True)

    mailer.send_email(subject, body)
    sys.exit(0)

# Extract phone number to send SMS to
to = incoming['To']
name, addr = parseaddr(to)

match = EMAIL_REGEX.search(addr)

if not match:
    # Invalid email address format
    from modules import smtp
    
    mailer = smtp.Mailer(cfg)

    subject = 'Invalid Phone Number'
    
    body = 'The phone number you specified in the email address is invalid.\n\n'
    body += 'Phone number must be 10 digits (area code + phone number). Please try again.\n'

    mailer.send_email(subject, body)
    sys.exit(0)

else:
    number = match.group(1)

for part in incoming.walk():
    if part.get_content_type() == 'text/plain':
        message = part.get_payload().splitlines()[0]

gv.send_sms(number, message)
