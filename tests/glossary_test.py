#coding: utf-8

import io
import os
import unittest
import tempfile, shutil
from hamcrest import *

import yomoyama
from yomoyama import glossary

class GlossaryTest(unittest.TestCase):
    def setUp(self):
        self.sut = glossary.Glossary(1)

    def test_single_word(self):
        self.sut.add_entry('test', u'テスト', 't1')
        assert_that(self.sut.get_entry('test'), is_([(u'テスト', ['t1'])]))

    def test_multiple_word(self):
        self.sut.add_entry('unit test', u'単体テスト', 't1')
        assert_that(self.sut.get_entry('unit test'), is_([(u'単体テスト', ['t1'])]))

    def test_multiple_word_with_symbols_for_search(self):
        self.sut.add_entry('unit test', u'単体テスト', 't1')
        assert_that(self.sut.get_entry('unit, "test"'), is_([(u'単体テスト', ['t1'])]))

    def test_multiple_word_with_symbols_for_entry(self):
        self.sut.add_entry('"unit"   test,', u'「単体」テスト。', 't1')
        assert_that(self.sut.get_entry('unit test'), is_([(u'単体テスト', ['t1'])]))

    def test_duplicate_entry_with_different_translation(self):
        self.sut.add_entry('unit test', u'単体テスト', 't1')
        self.sut.add_entry('unit test', u'ユニットテスト', 't1')
        assert_that(self.sut.get_entry('unit test'), is_([(u'単体テスト', ['t1']), (u'ユニットテスト', ['t1'])]))

    def test_duplicate_entry_with_same_translation(self):
        self.sut.add_entry('unit test', u'単体テスト', 't1')
        self.sut.add_entry('unit test', u'単体テスト', 't2')
        self.sut.add_entry('unit test', u'"単体"テスト', 't3')
        assert_that(self.sut.get_entry('unit test'), is_([(u'単体テスト', ['t1', 't2', 't3'])]))

    def test_get_all(self):
        '''
        The chief purpose of this test is to protect
        the exposed interface of get_all() from internal changes.
        That is, the current implementation of get_all() is
        just returning internal self.dic.
        '''
        self.sut.add_entry('test', u'テスト', 't1')
        self.sut.add_entry('test', u'テスト', 't2')
        self.sut.add_entry('test', u'試験', 't1')
        self.sut.add_entry('unit test', u'単体テスト', 't1')
        assert_that(self.sut.get_all(), is_({
            'test': [
                (u'テスト', ['t1', 't2']),
                (u'試験', ['t1'])],
            'unit test': [
                (u'単体テスト', ['t1'])],
            }))

class GlossaryOnFileTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        filename = os.path.join(self.tempdir, 'glossary.rst')
        self.sut = glossary.GlossaryOnFile(1, filename)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_ordering_same_entry(self):
        self.sut.add_entry('entry1', u'訳語1', 't1')
        self.sut.add_entry('entry1', u'訳語1-1', 't2')
        self.sut.add_entry('entry1', u'訳語1-1', 't3')
        self.sut.add_entry('entry1', u'訳語1-2', 't4')
        assert_that(self.sut.ordered_entries(), is_([
            ('entry1', [(u'訳語1', ['t1']), (u'訳語1-1', ['t2', 't3']), (u'訳語1-2', ['t4'])]),
        ]))

    def test_serialized(self):
        self.sut.add_entry('entry1', u'訳語1', 't1')
        self.sut.add_entry('entry1', u'訳語1-1', 't2')
        self.sut.add_entry('entry2', u'訳語2', 't3')
        self.sut.add_entry('entry1', u'訳語1', 't4')
        out = io.StringIO()
        self.sut._serialized(out, 'rst')
        ser = out.getvalue()
        assert_that(ser, is_(
u"""entry1
  - 訳語1
      - appears in: t1,t4
  - 訳語1-1
      - appears in: t2

entry2
  - 訳語2
      - appears in: t3

"""))

    def test_deserialize(self):
        ins = io.StringIO()
        ins.write(
u"""entry1
  - 訳語1
      - appears in: t1,t4
  - 訳語1-1
      - appears in: t2

entry2
  - 訳語2
      - appears in: t3

""")
        ins.seek(0)
        gl = glossary.GlossaryOnFile(1, None)
        gl._deserialize(ins, 'rst')

        assert_that(len(gl.dic), is_(2))
        assert_that(gl.get_entry('entry1'), is_([(u'訳語1', ['t1', 't4']), (u'訳語1-1', ['t2'])]))
        assert_that(gl.get_entry('entry2'), is_([(u'訳語2', ['t3'])]))

    def test_save_and_load(self):
        self.sut.add_entry('entry1', u'訳語1', 't1')
        self.sut.add_entry('entry1', u'訳語1-1', 't2')
        self.sut.add_entry('entry2', u'訳語2', 't3')
        self.sut.add_entry('entry1', u'訳語1', 't4')
        self.sut.save()

        gl = glossary.GlossaryOnFile(1, self.sut.filename)
        assert_that(self.sut.dic, is_(gl.dic))
