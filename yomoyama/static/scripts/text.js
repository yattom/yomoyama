$(function() {
  $('div.editor').hide();
  $('div.editor textarea').flexible();

  do_edit = function() {
    pId = $(this).data('pId');
    $('div[data-p-id=' + pId + '] .display').hide();
    $('div[data-p-id=' + pId + '] .editor').show();
    $('div[data-p-id=' + pId + '] .editor textarea').trigger('updateHeight');
  };
  $('span.edit').click(do_edit);

  do_save = function() {
    pId = $(this).data('pId');

    txt = $('div[data-p-id=' + pId + '] .editor textarea').val();
    $.ajax({
      url: $(location).attr('href') + '/paragraphs/' + pId,
      type: 'PUT',
      data: { text: txt },
      success: function() {
        $.get($(location).attr('href') + '/paragraphs/' + pId, function(data) {
          $('div[data-p-id=' + pId + ']').html('\
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
          $('div[data-p-id=' + pId + '] .display').show();
          $('div[data-p-id=' + pId + '] .editor').hide();
          $('div[data-p-id=' + pId + '] .editor textarea').flexible();
          $('div[data-p-id=' + pId + '] .editor span.edit').click(do_edit);
          $('div[data-p-id=' + pId + '] .editor span.save').click(do_save);
        });
      }
    });
  }
 
  $('span.save').click(do_save);
});
