from .external_dep import setup_external_dep
from .settingsdb import setup_settingsdb

def setup():
    setup_external_dep()
    setup_settingsdb()
    print("Setup complete")