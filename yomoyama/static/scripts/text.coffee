highlight_dict_entry = ->
  dictEntryId = $(this).data('dictEntryId')
  $('[data-dict-entry-id=' + dictEntryId + ']').addClass('dict-entry-highlight')

unhighlight_dict_entry = ->
  dictEntryId = $(this).data('dictEntryId')
  $('[data-dict-entry-id=' + dictEntryId + ']').removeClass('dict-entry-highlight')

build_en_part = (pId, original, dictionary) ->
  words = []
  for w, i in original
    word = $("<span data-w-id='" + i + "'>" + w + " </span>")
    words.push(word)
  for dic, i in dictionary
    for idx in [dic[0][0]...dic[0][1]]
      words[idx].addClass('in_dict')
      words[idx].attr('data-dict-entry-id', pId + '#' + i)
      if dic[1] != null
        words[idx].hover(highlight_dict_entry, unhighlight_dict_entry)
  div_en = $('div[data-p-id=' + pId + '] div.en span.word-count')
  div_en.before w for w in words

build_ja_part = (pId, original, dictionary) ->
  words = []
  for w, i in original
    word = $("<span data-w-id='" + i + "'>" + w + "</span>")
    words.push(word)
  for dic, i in dictionary
    if dic[1] == null
      continue
    for idx in [dic[1][0]...dic[1][1]]
      words[idx].addClass('in_dict')
      words[idx].attr('data-dict-entry-id', pId + '#' + i)
      words[idx].hover(highlight_dict_entry, unhighlight_dict_entry)
  div_ja = $('div[data-p-id=' + pId + '] div.ja div.display p')
  div_ja.append w for w in words

render_paragraph = (data) ->
  $('div[data-p-id=' + data.id + ']').html("""
<div class="en">
  <span class='word-count'>(#{data.words_so_far} / #{data.words})</span>
</div>
<div class="ja">
  <div class="display">
    <p></p>
    <span class="edit" data-p-id="#{data.id}">Edit</span>
  </div>
  <div class="editor">
    <textarea>#{data.translated.join('')}</textarea>
    <span class="save" data-p-id="#{data.id}">Save</span>
  </div>
</div>
""")
  build_en_part data.id, data.original, data.dictionary
  build_ja_part data.id, data.translated, data.dictionary
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

render_all_paragraph = (data) ->
  render_paragraph(para) for para in data.paragraphs

load_all_paragraphs = ->
  $.get $(location).attr('href') + '/paragraphs/all', render_all_paragraph

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
  load_all_paragraphs()
#  $('div.paragraph').each ->
#    pId = $(this).data('pId')
#    load_paragraph(pId)
