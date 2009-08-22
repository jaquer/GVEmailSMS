from distutils.core import setup
import py2exe, sys

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1,'compressed': 1, 'optimize': 2}},
    console = [{'script': "gvnotifier.py"}],
    zipfile = None
    )

setup(
    options = {'py2exe': {'bundle_files': 1,'compressed': 1, 'optimize': 2}},
    console = [{'script': "gvimapsms.py"}],
    zipfile = None
    )
