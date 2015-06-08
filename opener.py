import sublime, sublime_plugin
from os import path

SETTINGS_BASE_NAME = 'HiveOpener.sublime-settings'

class HiveOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.init()
        self.show_quick_panel()

    def init(self):
        settings = sublime.load_settings(SETTINGS_BASE_NAME)
        self.peek_file = settings.get('peek_file', False)
        self.items = []

        for key in ('dirs', 'files'):
            if not settings.has(key): continue
            self.items.extend(settings.get(key))

        if self.peek_file: self.save_view()

    def show_quick_panel(self):
        self.window.show_quick_panel(self.items, self.on_done, on_highlight=self.on_highlight)

    def on_done(self, index):
        if index == -1:
            return self.restore_view() if self.peek_file else self.noop()

        item_name = self.get_name_by_index(index)

        if path.isfile(item_name):
            self.open_file(item_name)
        elif path.isdir(item_name):
            self.open_dir(item_name)
        else:
            sublime.status_message('Invalid file/directory name: %s.' % item_name)

    def on_highlight(self, index):
        if not self.peek_file: return
        item_name = self.get_name_by_index(index)

        if self.peek_file and path.isfile(item_name):
            self.open_file(item_name, True)
        else:
            self.restore_view()

    def open_file(self, filename, preview=False):
        if preview:
            self.window.open_file(filename, sublime.TRANSIENT)
        else:
            self.window.open_file(filename)

    def open_dir(self, dirname):
        if sublime.platform() == 'windows':
            import subprocess
            subprocess.Popen(['explorer', dirname])
        elif sublime.platform() == 'osx':
            self.window.run_command('open_dir', { 'dir': dirname })

    def get_name_by_index(self, index):
        return self.items[index][0]

    # do nothing
    def noop(self): pass

    def save_view(self):
        self.saved_view = self.window.active_view()
        selection = self.saved_view.sel()
        # save region data as tuple so we can reverse serialization subsequently
        self.saved_regions = [(region.a, region.b) for region in selection]

        # return None if no selection(no viewable cursor)
        # otherwise we only care about the last region(regardless of multi-selection mode)
        return None if not len(selection) else selection[-1]

    def restore_view(self):
        saved_view = self.saved_view
        if saved_view == None: return

        # removes all regions currently if has any
        sublime.Selection.clear(saved_view)

        # restore previous saved regions
        for region in self.saved_regions:
            sublime.Selection.add(saved_view, sublime.Region(*region))

        # focus on previous saved view
        self.window.focus_view(saved_view)

        # scroll the view to center on the last region
        # saved_view.show_at_center(saved_view.sel()[-1])
