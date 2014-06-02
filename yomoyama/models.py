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

def readable_time(ms):
    '''
    >>> readable_time(8 * 1000)
    '0:08'
    >>> readable_time((6 * 60 + 40) * 1000)
    '6:40'
    >>> readable_time(45 * 1000)
    '0:45'
    >>> readable_time((6 * 60 + 40) * 1000)
    '6:40'
    >>> readable_time((30 * 60 + 25) * 1000)
    '30:25'
    >>> readable_time(((5 * 60 + 50) * 60 + 9) * 1000)
    '5:50:09'
    >>> readable_time(((246 * 60 + 50) * 60 + 9) * 1000)
    '246:50:09'
    '''
    sec = ms / 1000
    if sec < 60 * 60:
        return '%d:%02d'%(sec / 60, sec % 60)
    else:
        return '%d:%02d:%02d'%(sec / (60 * 60), (sec / 60) % 60, sec % 60)

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

    def get_wdir(self):
        book_for_user = BookForUser.query.filter_by(book_id=self.id, user_id=g.user.id).first()
        branch_name = book_for_user.remote_branch
        return WorkingDirectory(Book.book_dir(self.id), self.repo_url, branch_name, yomoyama.github_access_token())
    wdir = property(get_wdir)

    def commit_and_push(self, work_time_ms=0):
        self.wdir.add('*.yomo')
        self.wdir.commit_and_push(work_time_ms)

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


class BookForUser(Base):
    __tablename__ = 'books_for_users'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer)
    user_id = Column(Integer)
    remote_branch = Column(String(200))

    def __init__(self, book_id, user_id, remote_branch):
        self.book_id = book_id
        self.user_id = user_id
        self.remote_branch = remote_branch

@event.listens_for(BookForUser, 'after_insert')
def receive_after_insert(mapper, connection, book_for_user):
    book = Book.query.filter_by(id=book_for_user.book_id).first()
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
        self.git('checkout', '-b', self.remote_branch)
        self.git('pull', url_with_auth, self.remote_branch)

    def commit_and_push(self, work_time_ms=0):
        url_with_auth = 'https://' + self.access_token + '@' + self.repo_url[8:]
        self.git('add', '-u')
        comment = 'updated'
        if work_time_ms:
            comment += ' (%s)'%(readable_time(work_time_ms))
        self.git('commit', '-m', comment)
        self.git('push', url_with_auth, self.remote_branch)

    def pull(self):
        url_with_auth = 'https://' + self.access_token + '@' + self.repo_url[8:]
        self.git('pull', url_with_auth, self.remote_branch)

    def add(self, pattern):
        self.git('add', pattern)

    def git(self, *args):
        subprocess.call([app.config['GIT_CMD']] + list(args), cwd=self.dir_path)


init_db()
