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
        page.registerBook('T', 'R', 'B')
        report('2')

        waitFor(at(TopPage))
        report('3')
    }
}
