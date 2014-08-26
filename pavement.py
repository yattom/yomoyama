import sys
import os
from paver.easy import *
import subprocess

import tempfile

@task
def run():
    os.environ['PYTHONPATH'] = '.'
    os.environ['YOMOYAMA_CONFIG'] = '../local_config.py'
    sh('python yomoyama/run.py')

@task
def test_unit():
    sh('nosetests -s --with-doctest tests')

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
    sh('git branch work_test', cwd=repo_dir)
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

@task
@needs('test_unit', 'test_end2end')
def test():
    pass

@task
def install_coffee():
    os.environ['PREFIX'] = os.path.dirname(os.path.abspath(__file__))
    sh('wget http://nodejs.org/dist/v0.10.29/node-v0.10.29.tar.gz')
    sh('tar zxvf node-v0.10.29.tar.gz')
    sh('./configure --prefix=$PREFIX', cwd='node-v0.10.29')
    sh('make', cwd='node-v0.10.29')
    sh('make install', cwd='node-v0.10.29')
    sh('rm -rf node-v0.10.29 node-v0.10.29.tar.gz')
    sh('npm install coffee-script')
    sh('ln -s ../node_modules/coffee-script/bin/cake', cwd='bin')
    sh('ln -s ../node_modules/coffee-script/bin/coffee', cwd='bin')

@task
def coffee():
    sh('coffee --compile --map static/scripts/*.coffee', cwd='yomoyama')

@task
def coffeew():
    sh('coffee --compile --watch --map static/scripts/*.coffee', cwd='yomoyama')

@task
def devup():
    'run development supporting processes -- coffee, http server for test results, tail app.log'
    sh('screen -t coffee paver coffeew')
    sh('screen -t httpserver python -m SimpleHTTPServer')
    sh('screen screen tail -f app.log')
