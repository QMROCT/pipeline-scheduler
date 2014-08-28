import sys
import os

sys.path.insert(0, '/var/www/pipeline-scheduler/')
os.chdir('/var/www/pipeline-scheduler/')

from pipeline-scheduler import app as application
