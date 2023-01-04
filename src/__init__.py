import sys
import os

sys.path.append('.')
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
PROXY_PATH = os.path.abspath(os.path.join(PARENT_PATH, 'files'))
