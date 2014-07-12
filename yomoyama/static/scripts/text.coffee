render_paragraph = (data) ->
  en_text = ""
  for w, i in data.original
    if data.en_dictionary[i][0] != ''
      en_text += "<span data-w-id='" + i + "' class='in_dict'>" + w + "</span> "
    else
      en_text += "<span data-w-id='" + i + "'>" + w + "</span> "
  ja_text = ""
  ja_text += "<span data-w-id='" + i + "'>" + c + "</span>" for c, i in data.translated
  $('div[data-p-id=' + data.id + ']').html("""
<div class="en">
  #{en_text}
  <span>(#{data.words_so_far} / #{data.words})</span>
</div>
<div class="ja">
  <div class="display">
    <p>
      #{ja_text}
      <br>
    </p>
    <span class="edit" data-p-id="#{data.id}">Edit</span>
  </div>
  <div class="editor">
    <textarea>#{data.translated.join('')}</textarea>
    <span class="save" data-p-id="#{data.id}">Save</span>
  </div>
</div>
""")
#  for dict_entry in data.dictionary
#    en = dict_entry[0]
#    ja = dict_entry[1]
#    for i in [en[0]...en[1]]
#      $('div[data-p-id=' + data.id + '] .en span[data-w-id = ' + i + ']').css('color', 'red')
#    for i in [ja[0]...ja[1]]
#      $('div[data-p-id=' + data.id + '] .ja span[data-w-id = ' + i + ']').css('color', 'green')

  $('div[data-p-id=' + data.id + '] .display').show()
  $('div[data-p-id=' + data.id + '] .editor').hide()
  $('div[data-p-id=' + data.id + '] .editor textarea').flexible()
  $('div[data-p-id=' + data.id + '] span.edit').click(do_edit)
  $('div[data-p-id=' + data.id + '] span.save').click(do_save)
   
load_paragraph = (paragraph_id) ->
  $.get $(location).attr('href') + '/paragraphs/' + paragraph_id, render_paragraph

do_edit = ->
  pId = $(this).data('pId')
  $('div[data-p-id=' + pId + '] .display').hide()
  $('div[data-p-id=' + pId + '] .editor').show()
  $('div[data-p-id=' + pId + '] .editor textarea').trigger('updateHeight')
  $('div[data-p-id=' + pId + '] .editor').data('started_at', $.now())

do_save = ->
  pId = $(this).data('pId')

  started_at = $('div[data-p-id=' + pId + '] .editor').data('started_at')
  finished_at = $.now()
  txt = $('div[data-p-id=' + pId + '] .editor textarea').val()
  $.ajax
    url: $(location).attr('href') + '/paragraphs/' + pId
    type: 'PUT'
    data:
      text: txt
      paragraph_started_at: started_at
      paragraph_finished_at: finished_at
      session_started_at: $('body').data('session_started_at')
      session_saved_at: finished_at
    success: (resp) ->
      if(!resp.is_updated)
        $('div[data-p-id=' + resp.paragraph_id + '] .display').show()
        $('div[data-p-id=' + resp.paragraph_id + '] .editor').hide()
        return
      load_paragraph(resp.paragraph_id)

$ ->
  $('body').data('session_started_at', $.now())
  $('div.paragraph').each ->
    pId = $(this).data('pId')
    load_paragraph(pId)
