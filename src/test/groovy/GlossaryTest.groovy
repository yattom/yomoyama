import geb.*
import geb.junit4.*
import org.junit.Test

import org.junit.runner.RunWith
import org.junit.runners.JUnit4

@RunWith(JUnit4)
class GlossaryTest extends GebReportingTest {
    @Test
    void RegisterGlossaryEntryAndShow() {
        to TopPage
        newBookLink.click()

        at NewBookPage
        page.registerBook('GlossaryTest1', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        to TopPage
        bookByTitle('GlossaryTest1').click()
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

        driver.navigate().refresh()

        waitFor { glossary_for_paragraph[0].text().contains('English : 翻訳') }
        report()
    }

    @Test
    void MultipleWordsEntryForGlossary() {
        to TopPage
        newBookLink.click()

        at NewBookPage
        page.registerBook('GlossaryTest2', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        to TopPage
        bookByTitle('GlossaryTest2').click()
        waitFor { at FilesPage }
        files[0].click()
        at TextPage
        editAndSave(0, "翻訳文です。")

        selectEnText(0, 0, 0)
        assert glossary_en.text() == 'English'
        selectJaText(0, 0, 1)
        assert glossary_ja.text() == '翻訳'
        glossary_register.click()

        selectEnText(0, 0, 1)
        assert glossary_en.text() == 'English Paragraph'
        selectJaText(0, 0, 2)
        assert glossary_ja.text() == '翻訳文'
        glossary_register.click()
        report()

        driver.navigate().refresh()

        waitFor { glossary_for_paragraph[0].text().contains('English Paragraph : 翻訳文') }
        waitFor { glossary_for_paragraph[0].text().contains('English : 翻訳') }
        report()

    }

    @Test
    void NoDuplicateEntryInGlossaryForAParagraph() {
        to TopPage
        newBookLink.click()

        at NewBookPage
        page.registerBook('GlossaryTest3', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        to TopPage
        bookByTitle('GlossaryTest3').click()
        waitFor { at FilesPage }
        files[0].click()
        at TextPage
        editAndSave(1, "翻訳文です。2行目。3行目。")

        selectEnText(1, 3, 0)
        assert glossary_en.text() == 'Line'
        selectJaText(1, 7, 1)
        assert glossary_ja.text() == '行目'
        report()
        glossary_register.click()

        driver.navigate().refresh()

        waitFor { glossary_for_paragraph[1].text() == 'Line : 行目' }
        report()

    }
}

