import sys
import os
from paver.easy import *
import subprocess

import tempfile

@task
def test_end2end():
    os.environ['PYTHONPATH'] = '.'
    os.environ['YOMOYAMA_CONFIG'] = '../test_config.py'
    os.environ['TARGET_IP'] = target_ip = '127.0.0.1'
    os.environ['TARGET_PORT'] = target_port = '5001'
    tempdir = tempfile.mkdtemp()
    data_dir = os.path.join(tempdir, 'data')
    repo_dir = os.path.join(data_dir, 'repo')
    books_dir = os.path.join(data_dir, 'books')
    os.mkdir(data_dir)

    os.mkdir(repo_dir)
    sh('git init', cwd=repo_dir)
    txt = '''
English Paragraph 1.

English Paragraph 2.
Line 2.
Line 3.
'''
    with open(os.path.join(repo_dir, 'foo.txt'), 'w') as f:
        f.write(txt)
    sh('git add foo.txt', cwd=repo_dir)
    sh('git commit -m "initial"', cwd=repo_dir)
    os.environ['ORIGINAL_REPO_URL'] = repo_dir

    os.mkdir(books_dir)
    os.environ['BOOKS_DIR'] = books_dir
    os.environ['DISPLAY'] = ':1'
    devnull = open('/dev/null', 'w')
    x = subprocess.Popen(['Xvfb', os.environ['DISPLAY']], stdout=devnull, stderr=devnull)
    p = subprocess.Popen(['gunicorn','yomoyama.run:app', '-b', '%s:%s'%(target_ip, target_port), '--log-file', 'app.log', '--log-level', 'debug'])
    try:
        sh('./gradlew cleanTest firefoxTest')
    finally:
        p.terminate()
        x.terminate()
        devnull.close()
        sh('rm -rf %s'%(tempdir))
