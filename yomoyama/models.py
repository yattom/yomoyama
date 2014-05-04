import os
import os.path
import subprocess
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

    def initialize_repository(self):
        book_dir = Book.book_dir(self.id)
        assert os.access(book_dir, os.F_OK) == False, 'book working directory already exsits'
        url_with_auth = 'https://' + g.user.github_access_token + '@' + self.repo_url[8:]
        os.mkdir(book_dir)
        #branch = 'master'
        branch = 'yattom_working' #FIXME!!!
        # git operation is always pull (do not clone)
        # see https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth 
        subprocess.call([app.config['GIT_CMD'], 'init', '.'], cwd=book_dir)
        subprocess.call([app.config['GIT_CMD'], 'pull', url_with_auth, branch], cwd=book_dir)

    def commit_and_push(self):
        book_dir = Book.book_dir(self.id)
        url_with_auth = 'https://' + g.user.github_access_token + '@' + self.repo_url[8:]
        #branch = 'master'
        branch = 'yattom_working' #FIXME!!!
        subprocess.call([app.config['GIT_CMD'], 'add', '-u'], cwd=book_dir)
        subprocess.call([app.config['GIT_CMD'], 'commit', '-m', 'updated'], cwd=book_dir)
        subprocess.call([app.config['GIT_CMD'], 'push', url_with_auth, 'master:%s'%(branch)], cwd=book_dir)

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
    book.initialize_repository()

init_db()
