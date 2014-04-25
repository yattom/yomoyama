$(function() {
  $('div.editor').hide();
  $('div.editor textarea').flexible();

  enable_edit_button = function() {
    $('span.edit').click(function() {
      pId = $(this).data('pId');
      $('div[data-p-id=' + pId + '] .display').hide();
      $('div[data-p-id=' + pId + '] .editor').show();
      $('div[data-p-id=' + pId + '] .editor textarea').trigger('updateHeight');
    });
  };
  enable_edit_button();

  enable_save_button = function() {
    $('span.save').click(function() {
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
            enable_edit_button();
            enable_save_button();
          });
        }
      });
    });
  };
  enable_save_button();
});
