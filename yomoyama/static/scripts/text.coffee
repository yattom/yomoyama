class Glossary
  constructor: ->
    @glossary = {}

  update: (key, entries) ->
    if key not in @glossary
      @glossary[key] = []
    @glossary[key] = entries

  entry: (key) ->
    if @glossary[key] == undefined
      return []
    return @glossary[key]

glossary = new Glossary
glossary.update('team', ['チーム', 'スクラムチーム'])
glossary.update('Marcus', ['マーカス'])

highlight_dict_entry = ->
  dictEntryId = $(this).data('dictEntryId')
  $('[data-dict-entry-id=' + dictEntryId + ']').addClass('dict-entry-highlight')

unhighlight_dict_entry = ->
  dictEntryId = $(this).data('dictEntryId')
  $('[data-dict-entry-id=' + dictEntryId + ']').removeClass('dict-entry-highlight')

words_to_spans = (pId, original) ->
  words = []
  for w, i in original
    word = $('<span data-w-id="' + i + '">' + w + '</span>')
    words.push(word)
  return words

build_en_part = (pId, original, dictionary) ->
  words = words_to_spans(pId, (w + ' ' for w in original))
  for dic, i in dictionary
    for idx in [dic[0][0]...dic[0][1]]
      words[idx].addClass('in_dict')
      words[idx].attr('data-dict-entry-id', pId + '#' + i)
      if dic[1] != null
        words[idx].hover(highlight_dict_entry, unhighlight_dict_entry)
  div_en = $('div[data-p-id=' + pId + '] div.en span.word-count')
  div_en.before w for w in words

build_ja_part = (pId, original, dictionary) ->
  words = words_to_spans(pId, original)
  for dic, i in dictionary
    if dic[1] == null
      continue
    for idx in [dic[1][0]...dic[1][1]]
      words[idx].addClass('in_dict')
      words[idx].attr('data-dict-entry-id', pId + '#' + i)
      words[idx].hover(highlight_dict_entry, unhighlight_dict_entry)
  div_ja = $('div[data-p-id=' + pId + '] div.ja div.display p')
  div_ja.append w for w in words

apply_glossary_to_paragraph = (pId) ->
  found = {}
  $('div[data-p-id=' + pId + '] div.glossary').html('')
  $('div[data-p-id=' + pId + '] div.editor_glossary').html('')
  $('div[data-p-id=' + pId + '] div.en span').each ->
    word = $(this).text().trim()
    entries = glossary.entry(word)
    return if entries == undefined
    if entries.length > 0 and found[word] == undefined
      $("div[data-p-id=#{ pId }] div.glossary").append($("<div>#{ word } : #{entries}</div>"))
      edit = $("<div>#{ word } </div>")
      for e in entries
        btn = $("<button>#{e}</button>")
        btn.click ->
          t = $('div[data-p-id=' + pId + '] div.ja textarea').text()
          $('div[data-p-id=' + pId + '] div.ja textarea').text(t + e)
        edit.append(btn)
      $('div[data-p-id=' + pId + '] div.editor_glossary').append(edit)
      found[word] = 1
  if found.length == 0
    # prevent collapsing
    $('div[data-p-id=' + pId + '] div.glossary').html('&nbsp;')


render_paragraph = (data) ->
  $('div[data-p-id=' + data.id + ']').html("""
<div class="glossary">&nbsp;</div>
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
    <div class="editor_glossary"></div>
  </div>
</div>
""")
  build_en_part data.id, data.original, data.dictionary
  build_ja_part data.id, data.translated, data.dictionary
  apply_glossary_to_paragraph data.id
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

setup_selected_event_handlers = ->
  $('body').mouseup ->
    selection = window.getSelection()
    return if selection.toString() == ''
    if $(selection.getRangeAt(0).startContainer).closest('.en').length > 0
      $('#new_entry #original').text(selection.toString())
    if $(selection.getRangeAt(0).startContainer).closest('.ja').length > 0
      $('#new_entry #translated').text(selection.toString())
  $('#new_entry button#clear').click ->
    $('#new_entry #original').text('')
    $('#new_entry #translated').text('')
  $('#new_entry button#register').click ->
    original = encodeURIComponent($('#new_entry #original').text())
    $.ajax
      url: "/books/#{$('body').data('bookId')}/glossary/#{original}"
      type: 'PUT'
      data:
        original: $('#new_entry #original').text()
        translated: $('#new_entry #translated').text()
        text_id: $('body').data('textId')

$ ->
  $('body').data('session_started_at', $.now())
# FIXME: load all is awkwardly slow so don't use for now
#  load_all_paragraphs()
  $('div.paragraph').each ->
    pId = $(this).data('pId')
    load_paragraph(pId)
  setup_selected_event_handlers()

