import geb.*
import geb.junit4.*
import org.junit.Test

import org.junit.runner.RunWith
import org.junit.runners.JUnit4

@RunWith(JUnit4)
class TranslationPairsTest extends GebReportingTest {
    @Test
    void PairIsHighlighted() {
        to TopPage
        newBookLink.click()

        at NewBookPage
        page.registerBook('TranslationPairsTest1', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        to TopPage
        bookByTitle('TranslationPairsTest1').click()
        waitFor { at FilesPage }

        files[0].click()
        at TextPage
        editAndSave(0, "英語のパラグラフ1。")
        driver.navigate().refresh()

        assert original[0].find('span.has_pair').text() == 'English'
        assert translated[0].find('span.has_pair')[0].text() == '英'
        assert translated[0].find('span.has_pair')[1].text() == '語'
        report()
    }
}


