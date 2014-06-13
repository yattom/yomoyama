import sys
import os
from paver.easy import *
import subprocess

import tempfile

@task
def test_end2end():
    os.environ['PYTHONPATH']='.'
    os.environ['YOMOYAMA_CONFIG']='../test_config.py'
    os.environ['TARGET_IP']=target_ip='127.0.0.1'
    os.environ['TARGET_PORT']=target_port='5001'
    tempdir = tempfile.mkdtemp()
    data_dir = os.path.join(tempdir, 'data')
    books_dir = os.path.join(data_dir, 'books')
    os.mkdir(data_dir)
    os.mkdir(books_dir)
    os.environ['BOOKS_DIR']=books_dir
    os.environ['DISPLAY']=':1'
    x=subprocess.Popen(['Xvfb', os.environ['DISPLAY']])
    p=subprocess.Popen(['gunicorn','yomoyama.run:app', '-b', '%s:%s'%(target_ip, target_port)])
    sh('./gradlew cleanTest firefoxTest')
    p.terminate()
    x.terminate()
