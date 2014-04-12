#coding: utf-8

import unittest
import tempfile
from hamcrest import *

from trans_server import text

def assert_load_and_save(name, message=None):
    t = load_data(name)
    t.save()

    testdata = TEXT_FOR_TESTS[name]
    with open(t.path) as f:
        d = f.read()
        if type(testdata) is tuple and len(testdata) == 2:
            assert_that(d, equal_to(testdata[0]), testdata[1])
        else:
            assert_that(d, equal_to(testdata[0]))


def load_data(name):
    testdata = TEXT_FOR_TESTS[name]
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name
        f.write(testdata[0])

    try:
        return text.Text(fname)
    finally:
        f.unlink(f.name)

TEXT_FOR_TESTS = {
    'multi_para': (
u'''EnglishLine.
日本語の行

EnglishLine2.
'''.encode('utf-8'), 'multi paragraphs of single lines'),
    'multi_line': (
u'''
English Line 1.
English Line 2.
English Line 3.
日本語の行1。
日本語の行2。
日本語の行3。
'''.encode('utf-8'), 'a paragraph of multi lines'),
    'many_para': (
u'''English Paragraph 1.
With multi English lines.
日本語の段落1。

English Paragraph 2. Only English part.

English Paragraph 3.
日本語の段落1。
日本語部分が複数行。

日本語の段落4。日本語部分のみ。
'''.encode('utf-8'), 'several paragraphs'),
    'mixed_translated': (
u'''English Part.
日本語の行。
English line in translated part.
'''.encode('utf-8'), 'English-only lines in translated part'),
}

class TextTest(unittest.TestCase):
    def test_load_multi_para(self):
        t = load_data('multi_para')
        assert_that(len(t.paragraphs), is_(2))
        assert_that(t.paragraphs[0].original(), is_(u'EnglishLine.\n'))
        assert_that(t.paragraphs[0].translated(), is_(u'日本語の行\n'))
        assert_that(t.paragraphs[1].original(), is_('EnglishLine2.\n'))
        assert_that(t.paragraphs[1].translated(), is_(''))

    def test_load_many_para(self):
        t = load_data('many_para')
        assert_that(len(t.paragraphs), is_(4))
        assert_that(t.paragraphs[0].translated(), is_(u'日本語の段落1。\n'))
        assert_that(t.paragraphs[3].original(), is_(u''))

    def test_load_mixed_translated(self):
        t = load_data('mixed_translated')
        assert_that(t.paragraphs[0].original(), is_(u'English Part.\n'))

    def test_update_shorter(self):
        t = load_data('multi_para')
        t.paragraphs[0].translated().update(u'更新\n')
        assert_that(t.paragraphs[0].translated(), is_(u'更新\n'))
        assert_that(t.paragraphs[1].original(), is_('EnglishLine2.\n'))

    def test_update_longer(self):
        t = load_data('multi_para')
        t.paragraphs[0].translated().update(u'長い内容で更新した行。\n')
        assert_that(t.paragraphs[0].translated(), is_(u'長い内容で更新した行。\n'))
        assert_that(t.paragraphs[1].original(), is_('EnglishLine2.\n'))

    def test_load_and_save(self):
        '''
        Text must save contents exactly same as loaded.
        '''
        for key in TEXT_FOR_TESTS:
            assert_load_and_save(key)
