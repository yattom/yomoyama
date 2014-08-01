#encoding: utf-8

import re
import io
import os, os.path
from codecs import open

class Glossary(object):
    def __init__(self, book_id):
        self.book_id = book_id
        self.dic = {}

    def add_entry(self, original, translation, text_id):
        key = self._normalize(original)
        if not key in self.dic:
            self.dic[key] = []
        normalized_translation = self._normalize(translation)
        for t, tid in self.dic[key]:
            if t == normalized_translation:
                if text_id in tid: return
                tid.append(text_id)
                return
        self.dic[key].append((self._normalize(translation), [text_id]))

    def get_entry(self, phrase):
        key = self._normalize(phrase)
        if not key in self.dic: return []
        return self.dic[key]

    def _normalize(self, phrase):
        normalized = self._normalize_spaces(self._remove_symbols(phrase))
        return normalized

    def _normalize_spaces(self, phrase):
        symbols = re.compile(r' +')
        return symbols.sub(' ', phrase.strip())

    def _remove_symbols(self, phrase):
        symbols = re.compile(ur'[\'"(),.-/*!?―「」、。]')
        return symbols.sub('', phrase)


class GlossaryOnFile(Glossary):
    def __init__(self, book_id, filename):
        super(GlossaryOnFile, self).__init__(book_id)
        self.filename = filename
        if not filename: return
        if not os.path.exists(filename):
            # create the file with empty contents
            self.save()
        self.load()

    def ordered_entries(self):
        entries = []
        for key in sorted(self.dic.keys()):
            definitions = []
            for desc, tids in sorted(self.dic[key]):
                definitions.append((desc, tids))
            entries.append((key, definitions))
        return entries

    def _serialized(self, out, format):
        if format != 'rst':
            raise RuntimeError('not implemented')
        for key, defs in self.ordered_entries():
            out.write(u'%s\n'%(key))
            for desc, tids in defs:
                out.write(u'  - %s\n'%(desc))
                if tids:
                    out.write(u'      - appears in: %s\n'%(','.join([unicode(i) for i in tids])))
            out.write(u'\n')

    def _deserialize(self, ins, format):
        key = ''
        desc = ''
        tids = []
        def close_entry():
            if key and desc:
                for tid in tids:
                    self.add_entry(key, desc, tid)
        if format != 'rst':
            raise RuntimeError('not implemented')
        for line in (l.rstrip() for l in ins):
            if not line:
                close_entry()
                key = ''
                continue
            if not line.startswith(' '):
                close_entry()
                key = line
                desc = ''
                tids = []
                continue
            m = re.match('  - ([^ ].*)', line)
            if m:
                if not desc: close_entry()
                desc = m.group(1)
                continue
            m = re.match('      - appears in: (.*)', line)
            if m:
                tids = m.group(1).split(',')
                close_entry()
                desc = ''
                continue
        close_entry()

    def save(self):
        if not self.filename: return
        with open(self.filename, "w", encoding='utf8') as f:
            self._serialized(f, 'rst')

    def load(self):
        with open(self.filename, "r", encoding='utf8') as f:
            self._deserialize(f, 'rst')
