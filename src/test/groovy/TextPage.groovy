import geb.*

class TextPage extends Page {
    static at = { text.text() != "" }
    static content = {
        text { $('.paragraphs') }
        paragraphs { $('div.paragraph') }
        edit { $('span.edit') }
        translation_textbox { $('textarea') }
        save { $('span.save') }
        translated { $('div.ja') }
        original { $('div.en') }
    }
}


