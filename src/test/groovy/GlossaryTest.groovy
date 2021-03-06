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

        selectEnText(0, 0, 50)
        assert glossary_en.text() == 'English'
        selectJaText(0, 0, 20)
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

        selectEnText(0, 0, 50)
        assert glossary_en.text() == 'English'
        selectJaText(0, 0, 20)
        assert glossary_ja.text() == '翻訳'
        glossary_register.click()

        selectEnText(0, 0, 120)
        assert glossary_en.text() == 'English Paragraph'
        selectJaText(0, 0, 35)
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

        selectEnText(1, 145, 25)
        assert glossary_en.text() == 'Line'
        selectJaText(1, 90, 20)
        assert glossary_ja.text() == '行目'
        report()
        glossary_register.click()

        driver.navigate().refresh()

        waitFor { glossary_for_paragraph[1].text() == 'Line : 行目' }
        report()

    }

    @Test
    void UseGlossaryToEnterTranslationText() {
        to TopPage
        newBookLink.click()

        at NewBookPage
        page.registerBook('GlossaryTest4', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        to TopPage
        bookByTitle('GlossaryTest4').click()
        waitFor { at FilesPage }

        files[0].click()
        at TextPage
        editAndSave(0, "翻訳文です。")

        registerGlossaryEntry(0, 0, 50, 'English', 0, 20, '翻訳')
        edit[0].click()
        translation_textbox[0].value('これは')
        report()
        glossaryButton('翻訳').click()
        report()
        assert translation_textbox[0].value() == "これは翻訳"
    }

}

