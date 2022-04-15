import sys
import os

from dotenv import load_dotenv
load_dotenv()

path = os.getenv('APP_PATH')

if not path:
	print('Application path is not set!')
	sys.exit(1)

if not os.path.isdir(path):
	print('Application path does not exist!')
	sys.exit(1)

if path not in sys.path:
	sys.path.append(path)

from app import app as application
