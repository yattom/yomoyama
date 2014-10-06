// Generated by CoffeeScript 1.7.1
(function() {
  var Editor, Glossary, Paragraph, apply_glossary_to_paragraph, build_en_part, build_ja_part, do_edit, do_save, glossary, highlight_dict_entry, load_all_paragraphs, load_paragraph, render_all_paragraph, render_paragraph, setup_selected_event_handlers, unhighlight_dict_entry, view, words_to_spans,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  Glossary = (function() {
    function Glossary() {
      this.glossary = {};
    }

    Glossary.prototype.update = function(key, entries) {
      if (__indexOf.call(this.glossary, key) < 0) {
        this.glossary[key] = [];
      }
      return this.glossary[key] = entries;
    };

    Glossary.prototype.entry = function(key) {
      key = this.normalize(key);
      if (this.glossary[key] === void 0) {
        return [];
      }
      return this.glossary[key];
    };

    Glossary.prototype.entries_for_head = function(head) {
      var entries, k, v, words, _ref;
      head = this.normalize(head);
      entries = [];
      _ref = this.glossary;
      for (k in _ref) {
        v = _ref[k];
        words = k.split(' ');
        if (head === words[0]) {
          entries.push(k.trim());
        }
      }
      return entries;
    };

    Glossary.prototype.normalize = function(phrase) {
      phrase = phrase.replace(/[-\'"(),.\/*!?―「」、。]/, '');
      phrase = phrase.replace(/\s\s*/, ' ');
      return phrase;
    };

    Glossary.prototype.load = function() {
      var self;
      self = this;
      return $.ajax({
        url: "/books/" + ($('body').data('bookId')) + "/glossary",
        type: 'GET',
        success: function(resp) {
          var glossary_applied_pids, key, w, words;
          this.glossary = {};
          for (key in resp.glossary) {
            console.debug(key);
            words = (function() {
              var _i, _len, _ref, _results;
              _ref = resp.glossary[key];
              _results = [];
              for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                w = _ref[_i];
                _results.push(w[0]);
              }
              return _results;
            })();
            self.update(key, words);
          }
          glossary_applied_pids = {};
          return setInterval(function() {
            return $('div.paragraph').each(function() {
              var pId;
              pId = $(this).data('pId');
              if (glossary_applied_pids[pId] === void 0) {
                if ($(this).visible(true)) {
                  apply_glossary_to_paragraph(pId);
                  return glossary_applied_pids[pId] = 1;
                }
              }
            });
          }, 800);
        }
      });
    };

    return Glossary;

  })();

  glossary = new Glossary;

  Editor = (function() {
    function Editor(pid) {
      this.paragraph_id = pid;
    }

    Editor.prototype.saving = function(start) {
      if (start) {
        $('div[data-p-id=' + this.paragraph_id + '] .editor').addClass('saving');
        return $('div[data-p-id=' + this.paragraph_id + '] .editor textarea').attr('disabled', true);
      } else {
        $('div[data-p-id=' + this.paragraph_id + '] .editor textarea').attr('disabled', false);
        return $('div[data-p-id=' + this.paragraph_id + '] .editor').removeClass('saving');
      }
    };

    Editor.prototype.started_at = function() {
      return $('div[data-p-id=' + this.paragraph_id + '] .editor').data('started_at');
    };

    Editor.prototype.hide = function() {
      $('div[data-p-id=' + this.paragraph_id + '] .display').show();
      return $('div[data-p-id=' + this.paragraph_id + '] .editor').hide();
    };

    Editor.prototype.text = function() {
      return $('div[data-p-id=' + this.paragraph_id + '] .editor textarea').val();
    };

    return Editor;

  })();

  view = {
    Paragraph: Paragraph = (function() {
      function Paragraph(pid) {
        this.paragraph_id = pid;
        this.glossary_entries = [];
      }

      Paragraph.prototype.en_words = function(start, length) {
        var i, w, words, _i, _ref;
        words = '';
        for (i = _i = start, _ref = start + length; start <= _ref ? _i < _ref : _i > _ref; i = start <= _ref ? ++_i : --_i) {
          w = $('div[data-p-id=' + this.paragraph_id + '] div.en span:nth(' + i + ')').text().trim();
          words = words + ' ' + w;
        }
        return words.trim();
      };

      Paragraph.prototype.add_glossary_entry = function(words, translation) {
        var btn, edit, pid;
        if (this.glossary_entries.indexOf(glossary.normalize(words)) !== -1) {
          return;
        }
        this.glossary_entries.push(glossary.normalize(words));
        pid = this.paragraph_id;
        $("div[data-p-id=" + pid + "] div.glossary").append($("<div>" + words + " : " + translation + "</div>"));
        edit = $("<div>" + words + " </div>");
        btn = $("<button>" + translation + "</button>");
        btn.click(function() {
          var t;
          t = $('div[data-p-id=' + pid + '] div.ja textarea').text();
          return $('div[data-p-id=' + pid + '] div.ja textarea').text(t + translation);
        });
        edit.append(btn);
        return $('div[data-p-id=' + pid + '] div.editor_glossary').append(edit);
      };

      return Paragraph;

    })()
  };

  highlight_dict_entry = function() {
    var dictEntryId;
    dictEntryId = $(this).data('dictEntryId');
    return $('[data-dict-entry-id=' + dictEntryId + ']').addClass('dict-entry-highlight');
  };

  unhighlight_dict_entry = function() {
    var dictEntryId;
    dictEntryId = $(this).data('dictEntryId');
    return $('[data-dict-entry-id=' + dictEntryId + ']').removeClass('dict-entry-highlight');
  };

  words_to_spans = function(pId, original) {
    var i, w, word, words, _i, _len;
    words = [];
    for (i = _i = 0, _len = original.length; _i < _len; i = ++_i) {
      w = original[i];
      word = $('<span data-w-id="' + i + '">' + w + '</span>');
      words.push(word);
    }
    return words;
  };

  build_en_part = function(pId, original, translated_pairs) {
    var div_en, en_range, end, i, pair, range, ranges, start, words, _i, _j, _len, _len1;
    ranges = [];
    for (i = _i = 0, _len = translated_pairs.length; _i < _len; i = ++_i) {
      pair = translated_pairs[i];
      en_range = [pair[0][0], pair[0][1]];
      ranges.push([en_range, pId + '#' + i]);
    }
    words = original.slice(0);
    for (_j = 0, _len1 = ranges.length; _j < _len1; _j++) {
      range = ranges[_j];
      start = range[0][0];
      end = range[0][1];
      words[start] = '<span class="has_pair" data-dict-entry-id="' + range[1] + '">' + words[start];
      words[end] = '</span>' + words[end];
    }
    div_en = $('div[data-p-id=' + pId + '] div.en');
    div_en.prepend('<p>' + words.join(' ') + '</p>');
    return $('div[data-p-id=' + pId + '] span.has_pair').hover(highlight_dict_entry, unhighlight_dict_entry);
  };

  build_ja_part = function(pId, original, translated_pairs) {
    var div_en, en_range, end, i, pair, range, ranges, start, words, _i, _j, _len, _len1;
    ranges = [];
    for (i = _i = 0, _len = translated_pairs.length; _i < _len; i = ++_i) {
      pair = translated_pairs[i];
      if (pair[1] === null) {
        continue;
      }
      en_range = [pair[1][0], pair[1][1]];
      ranges.push([en_range, pId + '#' + i]);
    }
    words = original.slice(0);
    for (_j = 0, _len1 = ranges.length; _j < _len1; _j++) {
      range = ranges[_j];
      start = range[0][0];
      end = range[0][1];
      words[start] = '<span class="has_pair" data-dict-entry-id="' + range[1] + '">' + words[start];
      words[end] = '</span>' + words[end];
    }
    div_en = $('div[data-p-id=' + pId + '] div.ja div.display');
    div_en.prepend('<p>' + words.join('') + '</p>');
    return $('div[data-p-id=' + pId + '] span.has_pair').hover(highlight_dict_entry, unhighlight_dict_entry);
  };

  apply_glossary_to_paragraph = function(pId) {
    var entry, i, paragraph, word, words, _i, _len, _results;
    paragraph = new view.Paragraph(pId);
    $('div[data-p-id=' + pId + '] div.glossary').html('');
    $('div[data-p-id=' + pId + '] div.editor_glossary').html('');
    words = $('div[data-p-id=' + pId + '] div.en p').text().split(' ');
    _results = [];
    for (i = _i = 0, _len = words.length; _i < _len; i = ++_i) {
      word = words[i];
      word = word.trim();
      _results.push((function() {
        var _j, _len1, _ref, _results1;
        _ref = glossary.entries_for_head(word);
        _results1 = [];
        for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
          entry = _ref[_j];
          _results1.push((function(entry) {
            var ws;
            ws = words.slice(i, i + entry.split(' ').length).join(' ');
            if (ws === entry) {
              return paragraph.add_glossary_entry(ws, glossary.entry(ws));
            }
          })(entry));
        }
        return _results1;
      })());
    }
    return _results;
  };

  render_paragraph = function(data) {
    $('div[data-p-id=' + data.id + ']').html("<div class=\"glossary\">&nbsp;</div>\n<div class=\"en\">\n  <span class='word-count'>(" + data.words_so_far + " / " + data.words + ")</span>\n</div>\n<div class=\"ja\">\n  <div class=\"display\">\n    <p></p>\n    <span class=\"edit\" data-p-id=\"" + data.id + "\">Edit</span>\n  </div>\n  <div class=\"editor\">\n    <textarea>" + (data.translated.join('')) + "</textarea>\n    <span class=\"save\" data-p-id=\"" + data.id + "\">Save</span>\n    <div class=\"editor_glossary\"></div>\n  </div>\n</div>");
    build_en_part(data.id, data.original, data.translated_pairs);
    build_ja_part(data.id, data.translated, data.translated_pairs);
    apply_glossary_to_paragraph(data.id);
    $('div[data-p-id=' + data.id + '] .display').show();
    $('div[data-p-id=' + data.id + '] .editor').hide();
    $('div[data-p-id=' + data.id + '] .editor textarea').flexible();
    $('div[data-p-id=' + data.id + '] span.edit').click(do_edit);
    return $('div[data-p-id=' + data.id + '] span.save').click(do_save);
  };

  load_paragraph = function(paragraph_id) {
    return $.get($(location).attr('href') + '/paragraphs/' + paragraph_id, render_paragraph);
  };

  render_all_paragraph = function(data) {
    var para, _i, _len, _ref, _results;
    _ref = data.paragraphs;
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      para = _ref[_i];
      _results.push(render_paragraph(para));
    }
    return _results;
  };

  load_all_paragraphs = function() {
    return $.get($(location).attr('href') + '/paragraphs/all', render_all_paragraph);
  };

  do_edit = function() {
    var pId;
    pId = $(this).data('pId');
    $('div[data-p-id=' + pId + '] .display').hide();
    $('div[data-p-id=' + pId + '] .editor').show();
    $('div[data-p-id=' + pId + '] .editor textarea').trigger('updateHeight');
    return $('div[data-p-id=' + pId + '] .editor').data('started_at', $.now());
  };

  do_save = function() {
    var editor, finished_at, paragraph_id, started_at;
    paragraph_id = $(this).data('pId');
    editor = new Editor(paragraph_id);
    editor.saving(true);
    started_at = editor.started_at();
    finished_at = $.now();
    return $.ajax({
      url: $(location).attr('href') + '/paragraphs/' + paragraph_id,
      type: 'PUT',
      data: {
        text: editor.text(),
        paragraph_started_at: started_at,
        paragraph_finished_at: finished_at,
        session_started_at: $('body').data('session_started_at'),
        session_saved_at: finished_at
      },
      success: function(resp) {
        if (!resp.is_updated) {
          editor.hide();
          return;
        }
        return load_paragraph(resp.paragraph_id);
      },
      complete: function(xhr, status) {
        return editor.saving(false);
      }
    });
  };

  setup_selected_event_handlers = function() {
    $('body').mouseup(function() {
      var selection;
      selection = window.getSelection();
      if (selection.toString() === '') {
        return;
      }
      if ($(selection.getRangeAt(0).startContainer).closest('.en').length > 0) {
        $('#new_entry #original').text(selection.toString());
      }
      if ($(selection.getRangeAt(0).startContainer).closest('.ja').length > 0) {
        return $('#new_entry #translated').text(selection.toString());
      }
    });
    $('#new_entry button#clear').click(function() {
      $('#new_entry #original').text('');
      return $('#new_entry #translated').text('');
    });
    return $('#new_entry button#register').click(function() {
      var original;
      original = encodeURIComponent($('#new_entry #original').text());
      return $.ajax({
        url: "/books/" + ($('body').data('bookId')) + "/glossary/" + original,
        type: 'PUT',
        data: {
          original: $('#new_entry #original').text(),
          translated: $('#new_entry #translated').text(),
          text_id: $('body').data('textId')
        }
      });
    });
  };

  $(function() {
    $('body').data('session_started_at', $.now());
    $('div.paragraph').each(function() {
      var pId;
      pId = $(this).data('pId');
      return load_paragraph(pId);
    });
    glossary.load();
    return setup_selected_event_handlers();
  });

}).call(this);

//# sourceMappingURL=text.map
