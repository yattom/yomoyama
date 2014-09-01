import geb.*
import geb.junit4.*
import org.junit.Test

import org.junit.runner.RunWith
import org.junit.runners.JUnit4

@RunWith(JUnit4)
class GlossaryTest extends GebReportingTest {

    @Test
    void anExample() {
        to TopPage
        newBookLink.click()

        at NewBookPage
        page.registerBook('New Title', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        to TopPage
        availableBooks[0].click()
        waitFor { at FilesPage }

        files[0].click()
        at TextPage
        editAndSave(0, "翻訳文です。")

        selectEnText(0, 0, 0)
        assert glossary_en.text() == 'English'
        selectJaText(0, 0, 1)
        assert glossary_ja.text() == '翻訳'
        glossary_register.click()
        report()

        to TopPage
        availableBooks[0].click()
        waitFor { at FilesPage }
        files[0].click()
        at TextPage
        assert glossary_for_paragraph(0).text().contains('English : 翻訳')
        report()

        selectEnText(0, 0, 1)
        assert glossary_en.text() == 'English Paragraph'
        selectJaText(0, 0, 2)
        assert glossary_ja.text() == '翻訳文'
        glossary_register.click()
        assert glossary_for_paragraph(0).text().contains('English Paragraph : 翻訳文')
        report()

    }
}

