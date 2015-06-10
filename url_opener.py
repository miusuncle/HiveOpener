import sublime, sublime_plugin
import webbrowser

SETTINGS_BASE_NAME = 'HiveOpener.sublime-settings'

class HiveUrlOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.init()
        self.show_quick_panel()

    def init(self):
        settings = sublime.load_settings(SETTINGS_BASE_NAME)
        self.init_item_data(settings)

    def init_item_data(self, settings):
        self.items = settings.get('urls', [])
        self.view_items = []

        # sort items alphabetically
        self.items.sort(key=lambda x: x[1].lower())

        for item in self.items:
            url, desc = item
            desc = desc or url
            title = desc.ljust(100, ' ')
            subtitle = 'URL ' + url
            self.view_items.append([title, subtitle])

    def show_quick_panel(self):
        self.window.show_quick_panel(self.view_items, self.on_done)

    def on_done(self, index):
        if index == -1: return
        url = self.items[index][0]
        sublime.set_clipboard(url)
        sublime.status_message('URL Copied: ' + url)
        webbrowser.open_new_tab(url)
