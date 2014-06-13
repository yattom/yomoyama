import geb.*

class NewBookPage extends Page {
    static url = "/"
    static at = { title == "create new book - yomoyama" }
    static content = {
        newTitle { $('input', name: 'title') }
        repoUrl { $('input', name: 'repo_url') }
        branch { $('input', name: 'branch') }
    }

    void registerBook(newTitle_, repoUrl_, branch_) {
        newTitle.value(newTitle_)
        repoUrl.value(repoUrl_)
        branch.value(branch_)
        $('form input', type: 'submit').click()
    }
}
