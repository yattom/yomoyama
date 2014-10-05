class Glossary
  constructor: ->
    @glossary = {}

  update: (key, entries) ->
    if key not in @glossary
      @glossary[key] = []
    @glossary[key] = entries

  entry: (key) ->
    key = @normalize(key)
    if @glossary[key] == undefined
      return []
    return @glossary[key]

  entries_for_head: (head) ->
    head = @normalize(head)
    entries = []
    for k, v of @glossary
      words = k.split(' ')
      if head == words[0]
        entries.push(k.trim())
    return entries

  normalize: (phrase) ->
    phrase = phrase.replace(/[-\'"(),.\/*!?―「」、。]/, '')
    phrase = phrase.replace(/\s\s*/, ' ')
    return phrase

  load: ->
    self = this
    $.ajax
      url: "/books/#{$('body').data('bookId')}/glossary"
      type: 'GET'
      success: (resp) ->
        @glossary = {}
        for key of resp.glossary
          # omit text_id for now
          console.debug(key)
          words = (w[0] for w in resp.glossary[key])
          self.update(key, words)

        # start to let paragraphs apply glossary when visible
        glossary_applied_pids = {}
        setInterval ->
          $('div.paragraph').each ->
            pId = $(this).data('pId')
            if glossary_applied_pids[pId] == undefined
              if $(this).visible(true)
                apply_glossary_to_paragraph(pId)
                glossary_applied_pids[pId] = 1
        , 800


glossary = new Glossary

class Editor
  constructor: (pid) ->
    @paragraph_id = pid

  saving: (start) ->
    if start
      $('div[data-p-id=' + @paragraph_id + '] .editor').addClass('saving')
      $('div[data-p-id=' + @paragraph_id + '] .editor textarea').attr('disabled', true)
    else
      $('div[data-p-id=' + @paragraph_id + '] .editor textarea').attr('disabled', false)
      $('div[data-p-id=' + @paragraph_id + '] .editor').removeClass('saving')

  started_at: ->
    return $('div[data-p-id=' + @paragraph_id + '] .editor').data('started_at')

  hide: ->
    $('div[data-p-id=' + @paragraph_id + '] .display').show()
    $('div[data-p-id=' + @paragraph_id + '] .editor').hide()

  text: ->
    return $('div[data-p-id=' + @paragraph_id + '] .editor textarea').val()

view =
  Paragraph: class Paragraph
    constructor: (pid) ->
      @paragraph_id = pid
      @glossary_entries = []

    en_words: (start, length) ->
      words = ''
      for i in [start...(start + length)]
        w = $('div[data-p-id=' + @paragraph_id + '] div.en span:nth(' + i + ')').text().trim()
        words = words + ' ' + w
      return words.trim()

    add_glossary_entry: (words, translation) ->
      if @glossary_entries.indexOf(glossary.normalize(words)) != -1
        return
      @glossary_entries.push(glossary.normalize(words))
      pid = @paragraph_id
      $("div[data-p-id=#{ pid }] div.glossary").append($("<div>#{ words } : #{translation}</div>"))
      edit = $("<div>#{ words } </div>")
      btn = $("<button>#{translation}</button>")
      btn.click ->
        t = $('div[data-p-id=' + pid + '] div.ja textarea').text()
        $('div[data-p-id=' + pid + '] div.ja textarea').text(t + translation)
      edit.append(btn)
      $('div[data-p-id=' + pid + '] div.editor_glossary').append(edit)

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

build_en_part = (pId, original, translated_pairs) ->
  words = words_to_spans(pId, (w + ' ' for w in original))
  for dic, i in translated_pairs
    for idx in [dic[0][0]...dic[0][1]]
      words[idx].addClass('has_pair')
      words[idx].attr('data-dict-entry-id', pId + '#' + i)
      if dic[1] != null
        words[idx].hover(highlight_dict_entry, unhighlight_dict_entry)
  div_en = $('div[data-p-id=' + pId + '] div.en span.word-count')
  div_en.before w for w in words

build_ja_part = (pId, original, translated_pairs) ->
  words = words_to_spans(pId, original)
  for dic, i in translated_pairs
    if dic[1] == null
      continue
    for idx in [dic[1][0]...dic[1][1]]
      words[idx].addClass('has_pair')
      words[idx].attr('data-dict-entry-id', pId + '#' + i)
      words[idx].hover(highlight_dict_entry, unhighlight_dict_entry)
  div_ja = $('div[data-p-id=' + pId + '] div.ja div.display p')
  div_ja.append w for w in words

apply_glossary_to_paragraph = (pId) ->
  paragraph = new view.Paragraph(pId)
  $('div[data-p-id=' + pId + '] div.glossary').html('')
  $('div[data-p-id=' + pId + '] div.editor_glossary').html('')
  $('div[data-p-id=' + pId + '] div.en span').each ->
    head_text = $(this).text().trim()
    wId = $(this).data('wId')
    for entry in glossary.entries_for_head(head_text)
      do (entry) ->
        words = paragraph.en_words(wId, entry.split(' ').length)
        if words == entry
          paragraph.add_glossary_entry(words, glossary.entry(words))

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
  build_en_part data.id, data.original, data.translated_pairs
  build_ja_part data.id, data.translated, data.translated_pairs
  apply_glossary_to_paragraph data.id

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
  paragraph_id = $(this).data('pId')
  editor = new Editor(paragraph_id)

  editor.saving(true)
  started_at = editor.started_at()
  finished_at = $.now()
  $.ajax
    url: $(location).attr('href') + '/paragraphs/' + paragraph_id
    type: 'PUT'
    data:
      text: editor.text()
      paragraph_started_at: started_at
      paragraph_finished_at: finished_at
      session_started_at: $('body').data('session_started_at')
      session_saved_at: finished_at
    success: (resp) ->
      if(!resp.is_updated)
        editor.hide()
        return
      load_paragraph(resp.paragraph_id)
    complete: (xhr, status) ->
      editor.saving(false)

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
  glossary.load()
  setup_selected_event_handlers()
