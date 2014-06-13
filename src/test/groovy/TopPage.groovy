import geb.*

class TopPage extends Page {
    static url = "/"
    static at = { title == "yomoyama" }
    static content = {
        newBookLink { $("a", text: "本を登録") }
    }
}

