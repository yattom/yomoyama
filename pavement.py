import sys
import os
from paver.easy import *
import subprocess

@task
def test_end2end():
    os.environ['PYTHONPATH']='.'
    os.environ['YOMOYAMA_CONFIG']='../local_config.py'
    os.environ['DISPLAY']=':1'
    x=subprocess.Popen(['Xvfb', os.environ['DISPLAY']])
    p=subprocess.Popen(['gunicorn','yomoyama.run:app'])
    sh('./gradlew cleanTest firefoxTest')
    p.terminate()
    x.terminate()
