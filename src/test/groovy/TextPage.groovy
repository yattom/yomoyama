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

        glossary_en { $('div#glossary_area span#original') }
        glossary_ja { $('div#glossary_area span#translated') }
        glossary_register { $('div#glossary_area div#new_entry button#register') }
        glossary_for_paragraph { $('div.paragraph div.glossary') }
    }

    void editAndSave(idx, txt) {
        edit[idx].click()
        translation_textbox[idx].value(txt)
        save[idx].click()
        waitFor { translation_textbox[idx].displayed == false }
    }

    void selectEnText(paragraphId, from, len) {
        interact {
            moveToElement($('div.paragraph[data-p-id="' + paragraphId + '"] div.en span[data-w-id="' + from + '"]'), 0, 0)
            clickAndHold()
            moveToElement($('div.paragraph[data-p-id="' + paragraphId + '"] div.en span[data-w-id="' + (from + len + 1) + '"]'), -1, 0)
            release()
        }
    }

    void selectJaText(paragraphId, from, len) {
        interact {
            moveToElement($('div.paragraph[data-p-id="' + paragraphId + '"] div.ja span[data-w-id="' + from + '"]'), 0, 0)
            clickAndHold()
            moveToElement($('div.paragraph[data-p-id="' + paragraphId + '"] div.ja span[data-w-id="' + (from + len + 1) + '"]'), -1, 0)
            release()
        }
    }
}


