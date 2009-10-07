#!/usr/bin/env python

__appname__ = 'GVNotifier'
__version__ = '0.2'

# Constants
CFG_FILE = 'settings.cfg'
PWD_FILE = 'passwords.cfg'

import sys, time

import googlevoice
from lxml import etree

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
    
    # lxml parsing objects
    parser = etree.HTMLParser()
    xp_group_div  = etree.XPath('//div[@id=$id]')
    xp_group_rows = etree.XPath('.//div[@class="gc-message-sms-row"]')
    xp_msg_from   = etree.XPath('.//span[@class="gc-message-sms-from"]')
    xp_msg_text   = etree.XPath('.//span[@class="gc-message-sms-text"]')
    xp_msg_time   = etree.XPath('.//span[@class="gc-message-sms-time"]')

    # Mark all current message group ids as notified
    tree = etree.fromstring(gv.inbox_html(), parser)

    for id, group in gv.inbox()['messages'].iteritems():

        if group['isRead'] == False and 'sms' in group['labels']:
            group_div = xp_group_div(tree, id = id)[0]
            rows = xp_group_rows(group_div)
            notifications[id] = len(rows)
            
    print 'Current unread message groups: %s' % len(notifications)
    print 'Starting loop.'

    while True:

        # Why waste cycles unnecessarily?
        if gv.inbox()['unreadCounts']['sms'] == 0:
            time.sleep(60)
            continue

        tree = etree.fromstring(gv.inbox_html(), parser)

        for id, group in gv.inbox()['messages'].iteritems():

            if group['isRead'] == False and 'sms' in group['labels']:

                group_div = group_div = xp_group_div(tree, id = id)[0]

                rows = xp_group_rows(group_div)
                rows_count = len(rows)

                if not id in notifications:
                    notifications[id] = 0

                # New un-notified rows in group
                if notifications[id] != rows_count:

                    # Save count for next loop
                    notifications[id] = rows_count

                    senders  = xp_msg_from(group_div)
                    messages = xp_msg_text(group_div)
                    times    = xp_msg_time(group_div)

                    number = group['phoneNumber'].replace('+1', '', 1)
                    sender = senders[rows_count - 1].text.strip()[:-1]
                    subject = '%s - %s' % (sender, number)

                    print 'New SMS message from: %s' % number

                    # Create email message to send
                    body = ''
                    for index in reversed(range(rows_count)):
                        body += senders[index].text.strip() + ' '
                        body += messages[index].text.strip() + ' '
                        body += '(' + times[index].text.strip() + ')'
                        body += '\n'

                    mailer.send_email(subject, body)

        time.sleep(60)

if __name__ == '__main__':

    from httplib import IncompleteRead, BadStatusLine

    while True:
        try:
            print '%s v%s - Starting up.' % (__appname__, __version__)
            main()
        except KeyboardInterrupt:
            print 'Process cancelled. Exiting.'
            time.sleep(2)
            sys.exit(0)
        except (IncompleteRead, BadStatusLine):
            print 'Timeout while reading data from Google Voice. Restarting.'
            time.sleep(2)
        except:
            print 'Unexpected error. Exiting.'
            raise
