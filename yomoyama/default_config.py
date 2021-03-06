import os
base_dir = os.path.dirname(__file__)

# default configuration

BOOKS_DIR = base_dir + '/../data/books'
DATABASE_URI = 'sqlite:///' + base_dir + '/../data/sqlite.db'
SECRET_KEY = 'development key'

# configuration for GitHub-Flask
GITHUB_CLIENT_ID = 'your_client_id'
GITHUB_CLIENT_SECRET = 'your_client_secret'
GITHUB_CALLBACK_URL = 'http://localhost:5000/github-callback'

# configure git command
GIT_CMD = '/usr/bin/git'
