import os

# configuration for production on Docker

DATA_DIR = os.environ['YOMOYAMA_DATA_DIR']
BOOKS_DIR = DATA_DIR + '/books'
DATABASE_URI = 'sqlite:///' + DATA_DIR + '/sqlite.db'
SECRET_KEY = os.environ['SECRET_KEY']


# configuration for GitHub-Flask
GITHUB_CLIENT_ID = os.environ['CLIENT_ID']
GITHUB_CLIENT_SECRET = os.environ['CLIENT_SECRET']
GITHUB_CALLBACK_URL = 'http://yomoyama.yattom.jp/github-callback'

# configure git command
GIT_CMD = '/usr/bin/git'
