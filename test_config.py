import os

# configuration for automated tests

BOOKS_DIR = os.environ['BOOKS_DIR']
DATABASE_URI = 'sqlite://' # in-memory for testing
SECRET_KEY = 'TEST_SECRET_KEY'
LOGGED_IN_AS = 'test_user'

# configuration for GitHub-Flask
# Don't use GitHub when testing (replace with mock)
GITHUB_CLIENT_ID = 'NA'
GITHUB_CLIENT_SECRET = 'NA'
GITHUB_CALLBACK_URL = 'http://localhost:5001/github-callback'
