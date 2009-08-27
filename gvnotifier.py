#!/usr/bin/env python

__appname__ = 'GVNotifier'
__version__ = '0.2'

# Constants
CFG_FILE = 'settings.cfg'
PWD_FILE = 'passwords.cfg'

import sys, time

import googlevoice
from BeautifulSoup import BeautifulSoup

from modules import config, smtp

def main():

    cfg = config.Config(CFG_FILE, PWD_FILE)

    for section in 'google', 'smtp':
        cfg.read_password(section)

    mailer = smtp.Mailer(cfg)

    g = cfg['google']
    gv = googlevoice.Voice()
    gv.login(g['username'], g['password'])

    # Variable to hold notifications sent
    notifications = {}

    # Mark all current message group ids as notified
    parser = BeautifulSoup(gv.inbox_html())

    for id, group in gv.inbox()['messages'].iteritems():

        if group['isRead'] == False and 'sms' in group['labels']:
            rows = parser.find(id = id).findAll(attrs = {'class': 'gc-message-sms-row'})
            notifications[id] = len(rows)
            
    print 'Current unread message groups: %s' % len(notifications)
    print 'Starting loop.'

    while True:

        # Why waste cycles unnecessarily?
        if gv.inbox()['unreadCounts']['sms'] == 0:
            time.sleep(60)
            continue

        parser = BeautifulSoup(gv.inbox_html())

        for id, group in gv.inbox()['messages'].iteritems():

            if group['isRead'] == False and 'sms' in group['labels']:

                group_div = parser.find(id = id)

                rows = group_div.findAll(attrs = {'class': 'gc-message-sms-row'})
                rows_count = len(rows)

                if not id in notifications:
                    notifications[id] = 0

                # New un-notified rows in group
                if notifications[id] != rows_count:

                    # Save count for next loop
                    notifications[id] = rows_count

                    senders  = group_div.findAll(attrs = {'class': 'gc-message-sms-from'})
                    messages = group_div.findAll(attrs = {'class': 'gc-message-sms-text'})
                    times    = group_div.findAll(attrs = {'class': 'gc-message-sms-time'})

                    number = group['phoneNumber'].replace('+1', '', 1)
                    subject = 'SMS - %s' % number

                    print 'New SMS message from: %s' % number

                    # Create email message to send
                    body = ''
                    for index in reversed(range(rows_count)):
                        body += senders[index].string.strip() + ' '
                        body += messages[index].string.strip() + ' '
                        body += '(' + times[index].string.strip() + ')'
                        body += '\n'

                    mailer.send_email(subject, body)

        time.sleep(60)

if __name__ == '__main__':

    from httplib import IncompleteRead

    while True:
        try:
            print '%s v%s - Starting up.' % (__appname__, __version__)
            main()
        except KeyboardInterrupt:
            print 'Process cancelled. Exiting.'
            time.sleep(2)
            sys.exit(0)
        except IncompleteRead:
            print 'Timeout while reading data from Google Voice. Restarting.'
            time.sleep(2)
        except:
            print 'Unexpected error. Exiting.'
            raise
