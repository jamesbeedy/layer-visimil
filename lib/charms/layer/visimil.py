import os


VISIMIL_SNAP_CONFIG_DIR = \
    os.path.join('/', 'var', 'snap', 'visimil', 'common', 'config')

FLASK_SECRET_CONFIG = os.path.join(VISIMIL_SNAP_CONFIG_DIR, 'flask_secrets') 

VISIMIL_PORT = 5000
