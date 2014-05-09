#coding: utf-8

import os
import unittest
import tempfile, shutil
from hamcrest import *

from yomoyama import models

git_args = []
def mock_git(*args):
    git_args.append(args)

class WorkingDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_initialize_repository(self):
        sut = models.WorkingDirectory(self.tempdir + os.sep + 'wdir', 'https://exmaple.com/repo/.git', 'branch_name', 'auth_token')
        sut.git = mock_git
        sut.initialize_repository()

        assert_that(git_args[0], is_(('init', '.')))
        assert_that(git_args[1], is_(('pull', 'https://auth_token@exmaple.com/repo/.git', 'branch_name')))

    def test_initialize_repository_overwrite(self):
        os.mkdir(self.tempdir + os.sep + 'wdir')
        sut = models.WorkingDirectory(self.tempdir + os.sep + 'wdir', 'https://exmaple.com/repo/.git', 'branch_name', 'auth_token')
        sut.git = mock_git
        try:
            sut.initialize_repository()
            self.fail()
        except AssertionError, e:
            assert_that(e.message, is_('book working directory already exsits'))

