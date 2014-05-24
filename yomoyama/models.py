import os
import os.path
import subprocess
import yomoyama
from flask import g
from sqlalchemy import create_engine, Column, Integer, String, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from yomoyama import app

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    github_access_token = Column(Integer)

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    repo_url = Column(String(200))

    def __init__(self, title, repo_url):
        self.title = title
        self.repo_url = repo_url
        self.wdir = WorkingDirectory(Book.book_dir(self.id), self.repo_url, 'yattom_working', yomoyama.github_access_token())

    def commit_and_push(self):
        self.wdir.commit_and_push()

    def pull(self):
        self.wdir.pull()

    @staticmethod
    def book_dir(book_id):
        return app.config['BOOKS_DIR'] + os.sep + str(book_id)

    def texts(self):
        file_names = []
        def fn(arg, dirname, fnames):
            for f in fnames:
                if f.startswith('.'):
                    fnames.remove(f)
                    continue
                path = dirname[len(book_dir) + 1:] + os.sep if len(dirname) > len(book_dir) else ''
                path += f
                file_names.append(path)
            return True
        book_dir = Book.book_dir(self.id)
        os.path.walk(book_dir, fn, None)
        return file_names


@event.listens_for(Book, 'after_insert')
def receive_after_insert(mapper, connection, book):
    book.wdir.initialize_repository()


class WorkingDirectory(object):
    def __init__(self, dir_path, repo_url, remote_branch, access_token):
        self.dir_path = dir_path
        self.remote_branch = remote_branch
        self.repo_url = repo_url
        self.access_token = access_token

    def initialize_repository(self):
        assert os.access(self.dir_path, os.F_OK) == False, 'book working directory already exists'
        url_with_auth = 'https://' + self.access_token + '@' + self.repo_url[8:]
        os.mkdir(self.dir_path)
        # git operation is always pull (do not clone)
        # see https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth
        self.git('init', '.')
        self.git('pull', url_with_auth, self.remote_branch)

    def commit_and_push(self):
        url_with_auth = 'https://' + self.access_token + '@' + self.repo_url[8:]
        self.git('add', '-u')
        self.git('commit', '-m', 'updated')
        self.git('push', url_with_auth, 'master:%s'%(self.remote_branch))

    def pull(self):
        assert os.access(self.dir_path, os.F_OK) == False, 'book working directory already exists'
        url_with_auth = 'https://' + self.access_token + '@' + self.repo_url[8:]
        self.git('pull', url_with_auth, self.remote_branch)

    def git(self, *args):
        subprocess.call([app.config['GIT_CMD']] + list(args), cwd=self.dir_path)


init_db()
