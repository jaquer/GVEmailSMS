from ConfigParser import RawConfigParser
import base64

class Config:

    def __init__(self, cfg_file, pwd_file):
        
        self._cfg_file = cfg_file
        self._pwd_file = pwd_file
        
        cfg = {}
        config = RawConfigParser()
        config.read(cfg_file)

        for section in config.sections():
            cfg[section] = dict(config.items(section))
            
        # Split username and domain since it's used on incoming mail
        # regex (EMAIL_REGEX)
        cfg['email']['username'], cfg['email']['domain'] = cfg['email']['address'].split('@')

        # IMAP/SMTP usernames are optional
        for section in 'imap', 'smtp':
            if (not 'username' in cfg[section]) or (cfg[section]['username'] == ''):
                cfg[section]['username'] = cfg['email']['address']

        # Coerce boolean values
        bln = [('main', 'save_passwords'),
               ('main', 'debug'),
               ('imap', 'ssl'),
               ('smtp', 'ssl'),
               ('smtp', 'tls')]
        for section, setting in bln:
            cfg[section][setting] = config.getboolean(section, setting)
            
        # Read passwords
        config = RawConfigParser()
        config.read(pwd_file)
        if config.has_section('passwords'):
            for section, password in config.items('passwords'):
                cfg[section]['password'] = password

        if cfg['main']['debug']:
            cfg['DEBUG'] = True
        else:
            cfg['DEBUG'] = False
            
        del(cfg['main']['debug'])
            
        self._config = cfg

    def read_password(self, section):

        cfg = self._config

        if 'password' in cfg[section] and cfg[section]['password']:
            password = cfg[section]['password']
        else:
            # "Pretty Print" section names for prompt
            ppsections = {'google': 'Google Voice',
                          'imap': 'IMAP server',
                          'smtp': 'SMTP server'}

            import getpass
            password = getpass.getpass(ppsections[section] + ' password: ')
            password = base64.b64encode(password)

            if cfg['main']['save_passwords']:
                config = RawConfigParser()
                config.read(self._pwd_file)
                config.set('passwords', section, password)
                config.write(open(self._pwd_file, 'w'))

        self._config[section]['password'] = base64.b64decode(password)


    def __getitem__(self, section):
        return self._config[section]
        
if __name__ == '__main__':

    cfg = Config('..\\settings.cfg','..\\passwords.cfg')

    sections = 'main', 'google', 'email', 'imap', 'smtp'

    for section in sections:
        print section, cfg[section]
