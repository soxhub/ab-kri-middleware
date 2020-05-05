import os
import sys

# add the APP_DIR and ROOT_DIR to the sys path manually
# so we can use absolute imports throughout the app

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)

if not APP_DIR in sys.path:
    sys.path.insert(0, APP_DIR)

if not ROOT_DIR in sys.path:
    sys.path.insert(0, ROOT_DIR)
