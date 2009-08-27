from distutils.core import setup
import os, py2exe, sys

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'ascii': 1, 'bundle_files': 1,'compressed': 1, 'optimize': 2}},
    console = ['gvnotifier.py', 'gvimapsms.py'],
    data_files = ['settings.cfg.dist', 'passwords.cfg.dist']
    )

os.chdir('dist')
os.rename('settings.cfg.dist', 'settings.cfg')
os.rename('passwords.cfg.dist', 'passwords.cfg')
