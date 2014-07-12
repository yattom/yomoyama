// Generated by CoffeeScript 1.7.1
(function() {
  var do_edit, do_save, load_paragraph, render_paragraph;

  render_paragraph = function(data) {
    $('div[data-p-id=' + data.id + ']').html("<div class=\"en\">\n  " + data.original + "\n  <span>(" + data.words_so_far + " / " + data.words + ")</span>\n</div>\n<div class=\"ja\">\n  <div class=\"display\">\n    <p>\n      " + (data.translated.split('\n').join('<br>')) + "\n      <br>\n    </p>\n    <span class=\"edit\" data-p-id=\"" + data.id + "\">Edit</span>\n  </div>\n  <div class=\"editor\">\n    <textarea>" + data.translated + "</textarea>\n    <span class=\"save\" data-p-id=\"" + data.id + "\">Save</span>\n  </div>\n</div>");
    $('div[data-p-id=' + data.id + '] .display').show();
    $('div[data-p-id=' + data.id + '] .editor').hide();
    $('div[data-p-id=' + data.id + '] .editor textarea').flexible();
    $('div[data-p-id=' + data.id + '] span.edit').click(do_edit);
    return $('div[data-p-id=' + data.id + '] span.save').click(do_save);
  };

  load_paragraph = function(paragraph_id) {
    return $.get($(location).attr('href') + '/paragraphs/' + paragraph_id, render_paragraph);
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
