import os
base_dir = os.path.dirname(__file__)

# configuration for production on heroku

BOOKS_DIR = base_dir + '/data/books'
DATABASE_URI = 'sqlite:///' + base_dir + '/data/sqlite.db'
SECRET_KEY = os.environ['SECRET_KEY']

# configuration for GitHub-Flask
GITHUB_CLIENT_ID = os.environ['CLIENT_ID']
GITHUB_CLIENT_SECRET = os.environ['CLIENT_SECRET']
GITHUB_CALLBACK_URL = 'http://lit-depths-4578.herokuapp.com/github-callback'

# configure git command
GIT_CMD = '/usr/bin/git'
