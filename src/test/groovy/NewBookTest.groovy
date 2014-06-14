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
        page.registerBook('New Title', System.getenv('ORIGINAL_REPO_URL'), 'master')
        waitFor { $('body').text() == 'book: 1' }
        report('2')

        to TopPage
        assert availableBooks[0].text() == 'New Title'
        report('3')

        availableBooks[0].click()
        waitFor { at FilesPage }
        assert files[0].text() == 'foo.txt'
        report('4')
    }
}
