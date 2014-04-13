from codecs import open
import re

class Text(object):
    def __init__(self, path):
        self.path = path
        self.fragments = []
        with open(path, encoding='utf8') as f:
            self.read_raw(f.read())

    def read_raw(self, data):
        self.data = data
        lines = Text.split_into_lines(self.data)
        blocks = Text.split_into_blocks(self.data, lines)
        self.paragraphs = self.parse_into_paragraphs(lines, blocks)

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
            paragraph = Paragraph(self, original_span, translated_span)
            paragraphs.append(paragraph)
        return paragraphs

    @staticmethod
    def is_translated(line):
        return re.search(u'[^ 0-9a-zA-Z.,?!:;/$()\u2014\u201c\u201d\u2019\u005b-]', line.strip())

    def save(self):
        with open(self.path, 'wb', encoding='utf8') as f:
            f.write(self.data)

    def fragment(self, head, tail):
        f = TextFragment(self, head, tail)
        self.fragments.append(f)
        return f


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
            if not s.endswith('\n'):
                s += '\n'
            return s

    def __init__(self, text, original_span, translated_span):
        self.text = text
        self._original = self.text.fragment(*original_span)
        self._original.validator = Paragraph.OriginalPartValidator()
        self._original.normalizer = Paragraph.ParagraphNormalizer()
        self._translated = self.text.fragment(*translated_span)
        self._translated.validator = Paragraph.TranslatedPartValidator()
        self._translated.normalizer = Paragraph.ParagraphNormalizer()

    def original(self):
        if not self._original: return None
        return self._original

    def translated(self):
        if not self._translated: return None
        return self._translated


class TextFragment(object):
    def __init__(self, text, head, tail):
        self.text = text
        self.head = head
        self.tail = tail
        self.validator = None
        self.normalizer = None

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

    def __eq__(self, other):
        '''
        Enables comparing with str/unicode.  Convenient in tests.
        '''
        if isinstance(other, TextFragment):
            return (self.text == other.text and self.head == other.head and self.tail == other.tail)
        return unicode(self) == other
