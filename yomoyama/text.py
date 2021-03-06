import hashlib
from flask import json
from codecs import open
import re


def count_word(s):
    return len([w for w in re.split('\W+', s) if w])


class Text(object):

    def __init__(self, path):
        self.path = path
        self.fragments = []
        with open(path, encoding='utf8') as f:
            self.read_raw(f.read())
        try:
            with open(path + '.yomo', encoding='utf8') as f:
                self.metadata = json.load(f)
        except IOError:
            self.metadata = {}

    def read_raw(self, data):
        self.data = data
        lines = Text.split_into_lines(self.data)
        blocks = Text.split_into_blocks(self.data, lines)
        self.paragraphs = self.parse_into_paragraphs(lines, blocks)
        self.words = sum([p.words for p in self.paragraphs])

    @staticmethod
    def split_into_lines(data):
        lines = []
        head = 0
        for i, c in enumerate(data):
            if c == '\n':
                lines.append((head, i + 1))
                head = i + 1
        if lines[-1][1] < len(data):
            lines.append((head, len(data)))
        return lines

    @staticmethod
    def split_into_blocks(data, lines):
        blocks = []
        delimiter = True
        for i, (head, tail) in enumerate(lines):
            l = data[head:tail].strip()
            if len(l) == 0:
                delimiter = True
            else:
                if delimiter:
                    blocks.append([i, i])
                    delimiter = False
                else:
                    blocks[-1][1] = i
        return blocks

    def parse_into_paragraphs(self, lines, blocks):
        paragraphs = []
        paragraph_id = 0
        for start, end in blocks:
            first_translated = -1
            for idx in range(start, end + 1):
                head, tail = lines[idx]
                l = self.data[head:tail].strip()
                if Text.is_translated(l):
                    first_translated = idx
                    break
            if first_translated == -1:
                original_span = (lines[start][0], lines[end][1])
                translated_span = (lines[end][1], lines[end][1])
            else:
                original_span = (lines[start][0], lines[first_translated][0])
                translated_span = (lines[first_translated][0], lines[end][1])
            paragraph = Paragraph(paragraph_id, self, original_span, translated_span)
            paragraph.words_so_far = paragraph.words + sum([p.words for p in paragraphs])
            paragraphs.append(paragraph)
            paragraph_id += 1
        return paragraphs

    @staticmethod
    def is_translated(line):
        return re.search(u'[^ \[\]\'"0-9a-zA-Z+._,*&?!:;/$()=#%<>\u00d7\u00f1\u2013\u2014\u2018\u2019\u201c\u201d\u005b\u2022\u2026-]', line.strip()) is not None

    def save(self):
        with open(self.path, 'wb', encoding='utf8') as f:
            f.write(self.data)

    def export_translated(self):
        translated = []
        for para in self.paragraphs:
            translated.append(para.translated().value())
        return translated

    def fragment(self, head, tail):
        f = TextFragment(self, head, tail)
        self.fragments.append(f)
        return f

    def add_session(self, started_at, saved_at):
        if 'sessions' not in self.metadata:
            self.metadata['sessions'] = []
        sessions = self.metadata['sessions']
        for i in range(len(sessions)):
            if sessions[i][0] == started_at and sessions[i][1] < saved_at:
                sessions[i][1] = saved_at
                break
        else:
            sessions.append([started_at, saved_at])
        self.save_metadata()

    def save_metadata(self):
        with open(self.path + '.yomo', 'w', encoding='utf8') as f:
            json.dump(self.metadata, f)


class Paragraph(object):

    class OriginalPartValidator(object):

        def validate(self, s):
            if Text.is_translated(s):
                raise ValueError('validation failed: original part should not contain Japanese')

    class TranslatedPartValidator(object):

        def validate(self, s):
            lines = [l.strip() for l in s.split('\n')]
            if not Text.is_translated(lines[0]):
                raise ValueError('validation failed: the first line of a translated part should contain Japanese')

    class ParagraphNormalizer(object):

        def normalize(self, s):
            s = '\n'.join([l for l in s.split('\n') if len(l.strip()) > 0])
            if not s.endswith('\n'):
                s += '\n'
            return s

    def __init__(self, idx, text, original_span, translated_span):
        self.idx = idx
        self.text = text
        self._original = self.text.fragment(*original_span)
        self._original.validator = Paragraph.OriginalPartValidator()
        self._original.normalizer = Paragraph.ParagraphNormalizer()
        self._translated = self.text.fragment(*translated_span)
        self._translated.validator = Paragraph.TranslatedPartValidator()
        self._translated.normalizer = Paragraph.ParagraphNormalizer()
        self.words = count_word(unicode(self._original))

    def original(self):
        if not self._original: return None
        return self._original

    def translated(self):
        if not self._translated: return None
        return self._translated

    def get_id(self):
        return self.idx
    id = property(get_id)


class TextFragment(object):

    def __init__(self, text, head, tail):
        self.text = text
        self.head = head
        self.tail = tail
        self.validator = None
        self.normalizer = None
        self._id = None

    def value(self):
        return self.text.data[self.head:self.tail]

    def __str__(self):
        return self.value()

    def update(self, newtext):
        if self.validator: self.validator.validate(newtext)
        if self.normalizer: newtext = self.normalizer.normalize(newtext)
        self.text.data = self.text.data[:self.head] + newtext + self.text.data[self.tail:]
        old_len = self.tail - self.head
        new_len = len(newtext)
        self.tail = self.head + new_len
        for f in self.text.fragments:
            if f is self: continue
            if f.head >= self.head + old_len:
                f.head += new_len - old_len
            if f.tail > self.head + old_len:
                f.tail += new_len - old_len
        self._id = None

    def __eq__(self, other):
        '''
        Enables comparing with str/unicode.  Convenient in tests.
        '''
        if isinstance(other, TextFragment):
            return (self.text == other.text and self.head == other.head and self.tail == other.tail)
        return unicode(self) == other

    def get_id(self):
        if not self._id:
            self._id = hashlib.sha1(self.value().encode('utf8')).hexdigest()
        return self._id
    id = property(get_id)
