$ ->
  $('a.delete').click ->
    $.ajax
      url: "/books/#{$(this).data('bookId')}"
      type: 'DELETE'
      success: (resp) ->
        window.location.reload()
