#coding: utf-8

import os
import unittest
import tempfile, shutil
from hamcrest import *

import yomoyama
from yomoyama import models

git_args = []
def mock_git(*args):
    git_args.append(args)

class WorkingDirectoryTest(unittest.TestCase):
    def setUp(self):
        global git_args
        git_args = []
        self.tempdir = tempfile.mkdtemp()
        self.sut = models.WorkingDirectory(self.tempdir + os.sep + 'wdir', 'https://exmaple.com/repo/.git', 'branch_name', 'auth_token')
        self.sut.git = mock_git

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_initialize_repository(self):
        self.sut.initialize_repository()

        assert_that(git_args[0], is_(('init', '.')))
        assert_that(git_args[1], is_(('checkout', '-b', 'branch_name')))
        assert_that(git_args[2], is_(('pull', 'https://auth_token@exmaple.com/repo/.git', 'branch_name')))

    def test_initialize_repository_overwrite(self):
        os.mkdir(self.tempdir + os.sep + 'wdir')
        try:
            self.sut.initialize_repository()
            self.fail()
        except AssertionError, e:
            assert_that(e.message, is_('book working directory already exists'))
            assert_that(git_args, is_([]))

    def test_commit_and_push(self):
        self.sut.commit_and_push()

        assert_that(git_args[0], is_(('add', '-u')))
        assert_that(git_args[1], is_(('commit', '-m', 'updated')))
        assert_that(git_args[2], is_(('push', 'https://auth_token@exmaple.com/repo/.git', 'branch_name')))

    def test_commit_and_pull(self):
        self.sut.pull()

        assert_that(git_args[0], is_(('pull', 'https://auth_token@exmaple.com/repo/.git', 'branch_name')))
