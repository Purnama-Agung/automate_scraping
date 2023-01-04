from configparser import ConfigParser
from pathlib import Path
import sys
import os

sys.path.append('.')

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = Path(__file__).parents[2]
