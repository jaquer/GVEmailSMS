from distutils.core import setup
import os, py2exe, sys

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'ascii': 1, 'bundle_files': 1,'compressed': 1, 'optimize': 2}},
    console = ['gvnotifier.py', 'gvimapsms.py'],
    data_files = ['settings.cfg.dist', 'passwords.cfg.dist'],
    zipfile = 'modules.lib'
    )

os.chdir('dist')
for config in 'settings.cfg', 'passwords.cfg':
    if os.path.exists(config):
        os.remove(config)
    os.rename(config + '.dist', config)
