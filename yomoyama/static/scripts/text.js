$(function() {
  $('body').data('session_started_at', $.now());
  $('div.editor').hide();
  $('div.editor textarea').flexible();

  do_edit = function() {
    pId = $(this).data('pId');
    $('div[data-p-id=' + pId + '] .display').hide();
    $('div[data-p-id=' + pId + '] .editor').show();
    $('div[data-p-id=' + pId + '] .editor textarea').trigger('updateHeight');
    $('div[data-p-id=' + pId + '] .editor').data('started_at', $.now());
  };
  $('span.edit').click(do_edit);

  do_save = function() {
    pId = $(this).data('pId');

    started_at = $('div[data-p-id=' + pId + '] .editor').data('started_at');
    finished_at = $.now();
    txt = $('div[data-p-id=' + pId + '] .editor textarea').val();
    $.ajax({
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
        if(!resp.is_updated) {
          $('div[data-p-id=' + resp.paragraph_id + '] .display').show();
          $('div[data-p-id=' + resp.paragraph_id + '] .editor').hide();
          return;
        }
        $.get($(location).attr('href') + '/paragraphs/' + resp.paragraph_id, function(data) {
          $('div[data-p-id=' + data.id + ']').html('\
<div class="en">' + data.original + '</div>\
<div class="ja">\
  <div class="display">\
    <p>' + data.translated.split('\n').join('<br>') + '</p>\
    <span class="edit" data-p-id="' + data.id + '">Edit</span>\
  </div>\
  <div class="editor">\
    <textarea>' + data.translated + '</textarea>\
    <span class="save" data-p-id="' + data.id + '">Save</span>\
  </div>\
</div>\
');
          $('div[data-p-id=' + data.id + '] .display').show();
          $('div[data-p-id=' + data.id + '] .editor').hide();
          $('div[data-p-id=' + data.id + '] .editor textarea').flexible();
          $('div[data-p-id=' + data.id + '] span.edit').click(do_edit);
          $('div[data-p-id=' + data.id + '] span.save').click(do_save);
        });
      }
    });
  }
 
  $('span.save').click(do_save);
});
