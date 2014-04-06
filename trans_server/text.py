from codecs import open
import re

class Text(object):
    def __init__(self, path):
        self.path = path
        self.paragraphs = []
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


class Paragraph(object):
    def __init__(self, text):
        self.text = text
        self.original = None
        self.translated = None
        self.id = id(self)

    def append_translated(self, head, tail):
        if not self.translated:
            self.translated = (head, tail)
            return
        assert head == self.translated[1]
        self.translated = (self.translated[0], tail)

    def append_original(self, head, tail):
        if not self.original:
            self.original = (head, tail)
            return
        assert head == self.original[1]
        self.original = (self.original[0], tail)

    def original_text(self):
        if not self.original: return ''
        return self.text.data[self.original[0]:self.original[1]]

    def translated_text(self):
        if not self.translated: return ''
        return self.text.data[self.translated[0]:self.translated[1]]
