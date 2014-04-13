import os
import subprocess
from sqlalchemy import create_engine, Column, Integer, String, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from trans_server import app

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
        book_dir = app.config['BOOKS_DIR'] + os.sep + str(self.id)
        assert os.access(book_dir, os.F_OK) == False, 'book working directory already exsits'
        os.mkdir(book_dir)
        # git operation is always pull (do not clone)
        # see https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth 
        subprocess.call([app.config['GIT_CMD'], 'init', '.'], cwd=book_dir)
        subprocess.call([app.config['GIT_CMD'], 'pull', self.repo_url], cwd=book_dir)

@event.listens_for(Book, 'after_insert')
def receive_after_insert(mapper, connection, book):
    book.initialize_repository()

init_db()
