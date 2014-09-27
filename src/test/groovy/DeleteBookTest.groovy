import geb.*
import geb.junit4.*
import org.junit.Test

import org.junit.runner.RunWith
import org.junit.runners.JUnit4

@RunWith(JUnit4)
class DeleteBookTest extends GebReportingTest {

    @Test
    void anExample() {
        to TopPage
        newBookLink.click()
        report('1')

        at NewBookPage
        page.registerBook('DeleteMe', System.getenv('ORIGINAL_REPO_URL'), 'work_test')

        to TopPage
        assert bookByTitle('DeleteMe').displayed
        int idx = bookIndexByTitle('DeleteMe')
        report('2')

        deleteBooks[idx].click()
        to TopPage
        report('3')
        assert bookIndexByTitle('DeleteMe') == -1
    }
}

