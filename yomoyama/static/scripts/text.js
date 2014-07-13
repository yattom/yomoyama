// Generated by CoffeeScript 1.7.1
(function() {
  var build_en_part, build_ja_part, do_edit, do_save, highlight_dict_entry, load_all_paragraphs, load_paragraph, render_all_paragraph, render_paragraph, unhighlight_dict_entry;

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

  build_en_part = function(pId, original, dictionary) {
    var dic, div_en, i, idx, w, word, words, _i, _j, _k, _l, _len, _len1, _len2, _ref, _ref1, _results;
    words = [];
    for (i = _i = 0, _len = original.length; _i < _len; i = ++_i) {
      w = original[i];
      word = $("<span data-w-id='" + i + "'>" + w + " </span>");
      words.push(word);
    }
    for (i = _j = 0, _len1 = dictionary.length; _j < _len1; i = ++_j) {
      dic = dictionary[i];
      for (idx = _k = _ref = dic[0][0], _ref1 = dic[0][1]; _ref <= _ref1 ? _k < _ref1 : _k > _ref1; idx = _ref <= _ref1 ? ++_k : --_k) {
        words[idx].addClass('in_dict');
        words[idx].attr('data-dict-entry-id', pId + '#' + i);
        if (dic[1] !== null) {
          words[idx].hover(highlight_dict_entry, unhighlight_dict_entry);
        }
      }
    }
    div_en = $('div[data-p-id=' + pId + '] div.en span.word-count');
    _results = [];
    for (_l = 0, _len2 = words.length; _l < _len2; _l++) {
      w = words[_l];
      _results.push(div_en.before(w));
    }
    return _results;
  };

  build_ja_part = function(pId, original, dictionary) {
    var dic, div_ja, i, idx, w, word, words, _i, _j, _k, _l, _len, _len1, _len2, _ref, _ref1, _results;
    words = [];
    for (i = _i = 0, _len = original.length; _i < _len; i = ++_i) {
      w = original[i];
      word = $("<span data-w-id='" + i + "'>" + w + "</span>");
      words.push(word);
    }
    for (i = _j = 0, _len1 = dictionary.length; _j < _len1; i = ++_j) {
      dic = dictionary[i];
      if (dic[1] === null) {
        continue;
      }
      for (idx = _k = _ref = dic[1][0], _ref1 = dic[1][1]; _ref <= _ref1 ? _k < _ref1 : _k > _ref1; idx = _ref <= _ref1 ? ++_k : --_k) {
        words[idx].addClass('in_dict');
        words[idx].attr('data-dict-entry-id', pId + '#' + i);
        words[idx].hover(highlight_dict_entry, unhighlight_dict_entry);
      }
    }
    div_ja = $('div[data-p-id=' + pId + '] div.ja div.display p');
    _results = [];
    for (_l = 0, _len2 = words.length; _l < _len2; _l++) {
      w = words[_l];
      _results.push(div_ja.append(w));
    }
    return _results;
  };

  render_paragraph = function(data) {
    $('div[data-p-id=' + data.id + ']').html("<div class=\"en\">\n  <span class='word-count'>(" + data.words_so_far + " / " + data.words + ")</span>\n</div>\n<div class=\"ja\">\n  <div class=\"display\">\n    <p></p>\n    <span class=\"edit\" data-p-id=\"" + data.id + "\">Edit</span>\n  </div>\n  <div class=\"editor\">\n    <textarea>" + (data.translated.join('')) + "</textarea>\n    <span class=\"save\" data-p-id=\"" + data.id + "\">Save</span>\n  </div>\n</div>");
    build_en_part(data.id, data.original, data.dictionary);
    build_ja_part(data.id, data.translated, data.dictionary);
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
    var finished_at, pId, started_at, txt;
    pId = $(this).data('pId');
    started_at = $('div[data-p-id=' + pId + '] .editor').data('started_at');
    finished_at = $.now();
    txt = $('div[data-p-id=' + pId + '] .editor textarea').val();
    return $.ajax({
      url: $(location).attr('href') + '/paragraphs/' + pId,
      type: 'PUT',
      data: {
        text: txt,
        paragraph_started_at: started_at,
        paragraph_finished_at: finished_at,
        session_started_at: $('body').data('session_started_at'),
        session_saved_at: finished_at
      },
      success: function(resp) {
        if (!resp.is_updated) {
          $('div[data-p-id=' + resp.paragraph_id + '] .display').show();
          $('div[data-p-id=' + resp.paragraph_id + '] .editor').hide();
          return;
        }
        return load_paragraph(resp.paragraph_id);
      }
    });
  };

  $(function() {
    $('body').data('session_started_at', $.now());
    return $('div.paragraph').each(function() {
      var pId;
      pId = $(this).data('pId');
      return load_paragraph(pId);
    });
  });

}).call(this);
