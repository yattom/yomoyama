#coding: utf-8

import os
import unittest
import tempfile
from hamcrest import *

from yomoyama import text

def assert_load_and_save(name, message=None):
    t = load_data(name)
    try:
        t.save()

        testdata = TEXT_FOR_TESTS[name]
        with open(t.path) as f:
            d = f.read()
            if type(testdata) is tuple and len(testdata) == 2:
                assert_that(d, equal_to(testdata[0]), testdata[1])
            else:
                assert_that(d, equal_to(testdata[0]))
    finally:
        os.unlink(t.path)


def load_data(name):
    testdata = TEXT_FOR_TESTS[name]
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name
        f.write(testdata[0])

    try:
        return text.Text(fname)
    finally:
        f.unlink(f.name)

def block_to_str(data, lines, blocks):
    ps = [range(s, e + 1) for (s, e) in blocks]
    strs = [[data[lines[i][0]:lines[i][1]] for i in ls] for ls in ps]
    return [''.join(s) for s in strs]

def assert_reloaded_text_is_same(t):
    try:
        t.save()
        reloaded_text = text.Text(t.path)
        assert_that(reloaded_text.data, is_(t.data))

        assert_that(len(reloaded_text.paragraphs), is_(len(t.paragraphs)), 'reloaded text must have same number of paragraphs')
        for o, r in zip(t.paragraphs, reloaded_text.paragraphs):
            assert_that(o._original.value(), is_(r._original.value()), 'original part must be same')
            assert_that(o._translated.value(), is_(r._translated.value()), 'translated part must be same')
            assert_that(o._original.head, is_(r._original.head), 'original part must be same')
            assert_that(o._original.tail, is_(r._original.tail), 'original part must be same')
            assert_that(o._translated.head, is_(r._translated.head), 'translated part must be same')
            assert_that(o._translated.tail, is_(r._translated.tail), 'translated part must be same')
    finally:
        os.unlink(t.path)

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
    'whitespaces': (
u'''
  English Part.  
日本語の行。行末に空白。  

English Part. Trailing SPC and TAB.     
    先頭にTAB。  

'''.encode('utf-8'), 'Leading/Trailing SPC and TAB must remain'),
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

    def test_update_empty_translated_part(self):
        t = load_data('many_para')
        t.paragraphs[1].translated().update(u'空だった部分の日本語更新。\n')
        assert_that(t.paragraphs[1].translated(), is_(u'空だった部分の日本語更新。\n'))
        assert_that(t.paragraphs[1].original(), is_('English Paragraph 2. Only English part.\n'))

    def test_update_and_save_translated_part(self):
        t = load_data('many_para')
        t.paragraphs[0].translated().update(u'更新\n')
        assert_reloaded_text_is_same(t)

    def test_update_and_save_original_part(self):
        t = load_data('many_para')
        t.paragraphs[0].original().update(u'Updated English part.\n')
        assert_reloaded_text_is_same(t)

    def test_update_and_save_empty_translated_part(self):
        t = load_data('many_para')
        t.paragraphs[1].translated().update(u'空だった部分の日本語更新。\n')
        assert_reloaded_text_is_same(t)

    def test_update_and_save_empty_original_part(self):
        t = load_data('many_para')
        t.paragraphs[3].original().update(u'Updated empty-at-first original part\n')
        assert_reloaded_text_is_same(t)

    def test_update_and_save_no_newline_at_end(self):
        t = load_data('multi_para')
        t.paragraphs[0].translated().update(u'最初の行。\n最後の行に改行なし')
        assert_reloaded_text_is_same(t)

    def test_update_original_part_with_japanese(self):
        t = load_data('multi_para')
        before_data = t.data[:]
        try:
            t.paragraphs[0].original().update(u'日本語')
            self.fail('should not update original with Japanese')
        except ValueError:
            # ok
            pass
        assert_that(t.data, is_(before_data), 'data must not be changed after invalid update')

    def test_update_translated_with_first_line_only_english(self):
        t = load_data('multi_para')
        before_data = t.data[:]
        try:
            t.paragraphs[0].translated().update(u'English.\nあとは日本語\n')
            self.fail('should not update translated with only English top line.')
        except ValueError:
            # ok
            pass
        assert_that(t.data, is_(before_data), 'data must not be changed after invalid update')

    def test_update_translated_with_blankline(self):
        t = load_data('multi_para')
        before_data = t.data[:]
        t.paragraphs[0].translated().update(u'空行前。\n\n次は空白入り空行。\n  \n空行後。\n')
        assert_that(t.paragraphs[0].translated(), is_(u'空行前。\n次は空白入り空行。\n空行後。\n'), 'blank lines are removed')

    def test_update_translated_whitespaces_must_retained(self):
        t = load_data('multi_para')
        before_data = t.data[:]
        t.paragraphs[0].translated().update(u'  行頭空白\n行末空白  \n \t TABも\t  \n')
        assert_that(t.paragraphs[0].translated(), is_(u'  行頭空白\n行末空白  \n \t TABも\t  \n'))

    def test_load_and_save(self):
        '''
        Text must save contents exactly same as loaded.
        '''
        for key in TEXT_FOR_TESTS:
            assert_load_and_save(key)

    def test_split_into_blocks(self):
        data = "a\n\nb\nc\n\nd\ne\n"
        lines = text.Text.split_into_lines(data)
        assert_that([data[h:t] for (h, t) in lines],
                    is_(['a\n', '\n', 'b\n', 'c\n', '\n', 'd\n', 'e\n']))
        blocks = text.Text.split_into_blocks(data, lines)
        assert_that(block_to_str(data, lines, blocks), is_(['a\n', 'b\nc\n', 'd\ne\n']))

    def test_split_into_blocks_leading_blanks(self):
        data = "\n\na\n\nb\n"
        lines = text.Text.split_into_lines(data)
        blocks = text.Text.split_into_blocks(data, lines)
        assert_that(block_to_str(data, lines, blocks), is_(['a\n', 'b\n']))

    def test_split_into_blocks_trailing_blanks(self):
        data = "a\n\nb\n\n\n\n"
        lines = text.Text.split_into_lines(data)
        blocks = text.Text.split_into_blocks(data, lines)
        assert_that(block_to_str(data, lines, blocks), is_(['a\n', 'b\n']))

    def test_split_into_blocks_no_newline_at_end(self):
        data = "a\n\nb"
        lines = text.Text.split_into_lines(data)
        blocks = text.Text.split_into_blocks(data, lines)
        assert_that(block_to_str(data, lines, blocks), is_(['a\n', 'b']))

    def test_paragraph_id(self):
        t = load_data('multi_para')
        paragraph = t.paragraphs[0]
        id_before = paragraph.id
        paragraph.translated().update(u'更新')
        assert_that(paragraph.id, is_(id_before))
        paragraph.original().update(u'Modified')
        assert_that(paragraph.id, is_(id_before))

class TextWordCountTest(unittest.TestCase):
    def test_words(self):
        t = load_data('many_para')
        assert_that(t.paragraphs[0].words, is_(7))
        assert_that(t.paragraphs[0].words_so_far, is_(7))
        assert_that(t.paragraphs[1].words, is_(6))
        assert_that(t.paragraphs[1].words_so_far, is_(7 + 6))
        assert_that(t.paragraphs[2].words, is_(3))
        assert_that(t.paragraphs[2].words_so_far, is_(7 + 6 + 3))
        assert_that(t.paragraphs[3].words, is_(0))
        assert_that(t.paragraphs[3].words_so_far, is_(7 + 6 + 3 + 0))

class TextIsTranslated(unittest.TestCase):
    def test_english(self):
        assert_that(text.Text.is_translated('The quick brown fox jumps over a lazy dog.'), is_(False))

    def test_bullet(self):
        assert_that(text.Text.is_translated(u'•'), is_(False))

    def test_brackets(self):
        assert_that(text.Text.is_translated(u'[AUTHOR]'), is_(False))

    def test_titles(self):
        assert_that(text.Text.is_translated(u'#####'), is_(False))
        assert_that(text.Text.is_translated(u'====='), is_(False))
        assert_that(text.Text.is_translated(u'-----'), is_(False))

    def test_other_symbols(self):
        assert_that(text.Text.is_translated(u'+'), is_(False))

    def test_dash(self):
        assert_that(text.Text.is_translated(u'—'), is_(False))

    def test_quotes(self):
        assert_that(text.Text.is_translated(u'"\'“”’'), is_(False))

