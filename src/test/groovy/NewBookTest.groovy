import geb.*
import geb.junit4.*
import org.junit.Test

import org.junit.runner.RunWith
import org.junit.runners.JUnit4

@RunWith(JUnit4)
class NewBookTest extends GebReportingTest {

    @Test
    void anExample() {
        to TopPage
        newBookLink.click()
        report('1')

        at NewBookPage
        page.registerBook('New Title', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        at TopPage
        assert availableBooks[0].text() == 'New Title'
        report('3')

        availableBooks[0].click()
        waitFor { at FilesPage }
        assert files[0].text() == 'foo.txt'
        report('4')

        // 最初の訳文を入れる
        files[0].click()
        at TextPage
        edit[0].click()
        assert translation_textbox[0].displayed == true
        translation_textbox[0].value("翻訳文です。")
        report('5')
        save[0].click()
        waitFor { translation_textbox[0].displayed == false }
        assert translation_textbox[0].displayed == false
        assert translated[0].text() == "翻訳文です。\nEdit"

        // 訳文を変更する
        edit[0].click()
        assert translation_textbox[0].displayed == true
        assert translation_textbox[0].text() == "翻訳文です。"
        translation_textbox[0].value("直した翻訳文です。")
        report('6')
        save[0].click()
        waitFor { translation_textbox[0].displayed == false }
        assert translation_textbox[0].displayed == false
        assert translated[0].text() == "直した翻訳文です。\nEdit"

        // 次の段落の訳文を入れる
        edit[1].click()
        translation_textbox[1].value("第二段落です。")
        report('7')
        save[1].click()
        waitFor { translation_textbox[1].displayed == false }
        assert translated[1].text() == "第二段落です。\nEdit"

        // 次の段落の訳文を直す
        edit[1].click()
        translation_textbox[1].value("直した第二段落です。")
        report('9')
        save[1].click()
        waitFor { translation_textbox[1].displayed == false }
        assert translated[1].text() == "直した第二段落です。\nEdit"
    }
}
