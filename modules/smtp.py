import smtplib
from email.mime.text import MIMEText

class Mailer:

    def __init__(self, cfg):

        e = cfg['email']
        m = cfg['main']
        s = cfg['smtp']
        
        self._from = '%s@%s' % (e['username'], e['domain'])
        self._from_hdr = '%s <%s>' % (e['name'], self._from)
        
        self._to = m['notify']
        self._to_hdr = '<%s>' % self._to

        self._server = s['server']
        self._port   = s['port']
        self._username = s['username']
        self._password = s['password']

        self._tls = s['tls']

        if s['ssl']:
            self._smtp = smtplib.SMTP_SSL()
        else:
            self._smtp = smtplib.SMTP()

        if cfg['DEBUG']:
            self._smtp.set_debuglevel(1)

    def send_email(self, subject, body, number = ''):

        msg = MIMEText(body)
        
        from_hdr = self._from_hdr
        
        if number:
            from_hdr = from_hdr.replace('@', '+' + number + '@', 1)
        
        msg['From']    = from_hdr
        msg['To']      = self._to_hdr
        msg['Subject'] = subject
        
        self._smtp.connect(self._server, self._port)
        self._smtp.ehlo()
        if self._tls:
            self._smtp.starttls()
            self._smtp.ehlo()
        # Some SMTP servers don't require auth
        if self._username and self._password:
            self._smtp.login(self._username, self._password)
        self._smtp.sendmail(self._from, self._to, msg.as_string())
        self._smtp.quit()
