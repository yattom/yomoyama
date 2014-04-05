$(function() {
  $('div.editor').hide();
  $('div.editor textarea').flexible();

  $('span.edit').click(function() {
    pId = $(this).data('pId');
    $('div[data-p-id=' + pId + '] .display').hide();
    $('div[data-p-id=' + pId + '] .editor').show();
    $('div[data-p-id=' + pId + '] .editor textarea').trigger('updateHeight');
  });

  $('span.save').click(function() {
    pId = $(this).data('pId');
    $('div[data-p-id=' + pId + '] .display').show();
    $('div[data-p-id=' + pId + '] .editor').hide();

    txt = $('div[data-p-id=' + pId + '] .editor textarea').val();
    $.ajax({
      url: $(location).attr('href') + '/paragraphs/' + pId,
      type: 'PUT',
      data: { text: txt }
    });

  });
});
