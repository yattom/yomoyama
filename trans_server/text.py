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
        self.paragraphs = self.parse_into_paragraphs(lines)

    def parse_into_paragraphs(self, lines):
        paragraphs = []
        original_span = [0, 0]
        translated_span = [0, 0]
        for (head, tail) in lines:
            l = self.data[head:tail].strip()
            if len(l) == 0:
                paragraph = Paragraph(self, original_span, translated_span)
                paragraphs.append(paragraph)
                original_span = [tail, tail]
                translated_span = [tail, tail]
                continue
            if original_span[1] < head or Text.is_translated(l):
                if translated_span[0] < original_span[1]:
                    translated_span[0] = head
                translated_span[1] = tail
            else:
                original_span[1] = tail
                translated_span = [tail, tail]
        if original_span != [tail, tail] or translated_span != [tail, tail]:
            paragraph = Paragraph(self, original_span, translated_span)
            paragraphs.append(paragraph)
        return paragraphs

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
    def __init__(self, text, original_span, translated_span):
        self.text = text
        self._original = self.text.fragment(*original_span)
        self._translated = self.text.fragment(*translated_span)

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

    def value(self):
        return self.text.data[self.head:self.tail]

    def __str__(self):
        return self.value()

    def update(self, newtext):
        self.text.data = self.text.data[:self.head] + newtext + self.text.data[self.tail:]
        old_len = self.tail - self.head
        new_len = len(newtext)
        for f in self.text.fragments:
            if f.head >= self.head + old_len:
                f.head += new_len - old_len
            if f.tail >= self.head + old_len:
                f.tail += new_len - old_len

    def __eq__(self, other):
        '''
        Enables comparing with str/unicode.  Convenient in tests.
        '''
        if isinstance(other, TextFragment):
            return (self.text == other.text and self.head == other.head and self.tail == other.tail)
        return unicode(self) == other
