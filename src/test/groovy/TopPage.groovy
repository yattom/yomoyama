import geb.*

class TopPage extends Page {
    static url = "/"
    static at = { title == "yomoyama" }
    static content = {
        newBookLink { $("a", text: "本を登録") }
        availableBooks { $("ul.available_books a.title") }
        deleteBooks { $("ul.available_books .delete") }
    }

    def bookByTitle(name) {
        int idx = bookIndexByTitle(name)
        if (idx == -1) {
            assert False, 'no book named "' + name + '"'
        }
        return availableBooks[idx]
    }

    def bookIndexByTitle(name) {
        for (int i = 0; i < availableBooks.size(); i++) {
            if (availableBooks[i].text() == name) {
                return i
            }
        }
        return -1
    }
}
