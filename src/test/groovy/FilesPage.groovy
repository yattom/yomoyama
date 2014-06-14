import geb.*

class FilesPage extends Page {
    static at = { title.endsWith(" - yomoyama") }
    static content = {
        files { $('ul.files a') }
    }
}

