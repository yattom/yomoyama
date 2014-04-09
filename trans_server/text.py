from codecs import open
import re

class Text(object):
    def __init__(self, path):
        self.path = path
        self.paragraphs = []
        self.fragments = []
        with open(path, encoding='utf8') as f:
            self.data = f.read()

        lines = []
        head = 0
        for i, c in enumerate(self.data):
            if c == '\n':
                lines.append((head, i + 1))
                head = i + 1
        if lines[-1][1] < len(self.data):
            lines.append((head, len(self.data)))

        paragraph = None
        for (head, tail) in lines:
            l = self.data[head:tail]
            if not paragraph: paragraph = Paragraph(self)
            l = l.strip()
            if len(l) == 0:
                if paragraph:
                    self.paragraphs.append(paragraph)
                paragraph = None
                continue
            if Text.is_translated(l):
                paragraph.append_translated(head, tail)
            else:
                paragraph.append_original(head, tail)
        if paragraph:
            self.paragraphs.append(paragraph)

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
    def __init__(self, text):
        self.text = text
        self._original = None
        self._translated = None
        self.id = id(self)

    def append_translated(self, head, tail):
        if not self._translated:
            self._translated = self.text.fragment(head, tail)
            return
        assert head == self._translated.tail
        self._translated = self.text.fragment(self._translated.head, tail)

    def append_original(self, head, tail):
        if not self._original:
            self._original = self.text.fragment(head, tail)
            return
        assert head == self._original.tail
        self._original = self.text.fragment(self._original.head, tail)

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

    def __str__(self):
        return self.text.data[self.head:self.tail]

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
        Enables to compare with str/unicode.  Convenient in tests.
        '''
        if isinstance(other, TextFragment):
            return (self.text == other.text and self.head == other.head and self.tail == other.tail)
        return unicode(self) == other
