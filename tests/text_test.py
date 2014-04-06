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
    'multi_para': (u'EnglishLine.\n日本語の行\n\nEnglishLine2.\n\n'.encode('utf-8'), 'multi paragraphs of single lines'),
    'multi_line': (
u'''
English Line 1.
English Line 2.
English Line 3.
日本語の行1。
日本語の行2。
日本語の行3。
'''),
}

class TextLoadAndSaveTest(unittest.TestCase):
    '''
    Text must save contents exactly same as loaded.
    '''
    def test_multiparagraphs(self):
        assert_load_and_save('multi_para')


class TextTest(unittest.TestCase):
    def test_load_multi_para(self):
        t = load_data('multi_para')
        assert_that(len(t.paragraphs), is_(2))
        assert_that(t.paragraphs[0].original_text(), is_('EnglishLine.\n'))
        assert_that(t.paragraphs[0].translated_text(), is_(u'日本語の行\n'))
        assert_that(t.paragraphs[1].original_text(), is_('EnglishLine2.\n'))
        assert_that(t.paragraphs[1].translated_text(), is_(''))

