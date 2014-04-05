from codecs import open
import re

class Text(object):
    def __init__(self, path):
        self.paragraphs = []
        with open(path, encoding='utf8') as f:
            paragraph = None
            for l in f.readlines():
                if not paragraph: paragraph = Paragraph()
                l = l.strip()
                if len(l) == 0:
                    if paragraph:
                        self.paragraphs.append(paragraph)
                    paragraph = None
                    continue
                if re.search(u'[^ 0-9a-zA-Z.,?!:;/$()\u2014\u201c\u201d\u2019\u005b-]', l):
                    paragraph.append_translated(l)
                else:
                    paragraph.append_original(l)
            if paragraph:
                self.paragraphs.append(paragraph)

class Paragraph(object):
    def __init__(self):
        self.original_lines = []
        self.translated_lines = []

    def append_translated(self, line):
        self.translated_lines.append(line)

    def append_original(self, line):
        self.original_lines.append(line)

