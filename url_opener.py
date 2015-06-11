import sublime, sublime_plugin
import webbrowser

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class HiveUrlOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.init_item_data()
        self.show_quick_panel()

    def init_item_data(self):
        conf = sublime.load_settings(CONFIG_BASE_NAME)
        self.items = conf.get('urls', [])
        self.view_items = []

        # sort items alphabetically
        self.items.sort(key=lambda x: x[1].lower())

        for (url, desc) in self.items:
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

        if url[0:3] == 'www': url = 'http://' + url
        webbrowser.open_new_tab(url)
