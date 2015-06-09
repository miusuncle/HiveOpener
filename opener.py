import sublime, sublime_plugin
import subprocess
from os import path

SETTINGS_BASE_NAME = 'HiveOpener.sublime-settings'
USER_PLATFORM = sublime.platform()

class HiveOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.init()
        self.show_quick_panel()

    def init(self):
        settings = sublime.load_settings(SETTINGS_BASE_NAME)
        self.peek_file = settings.get('peek_file_on_highlight', False)
        self.binfile_open_in_subl = settings.get('open_binary_file_in_sublime', False)
        self.init_item_data(settings)

        if self.peek_file: self.save_view()

    def init_item_data(self, settings):
        self.items = []
        self.view_items = []

        for key in ('dirs', 'files'):
            if not settings.has(key): continue
            self.items.extend(settings.get(key))

        # sort items alphabetically
        self.items.sort(key=lambda x: x[1].lower())

        for item in self.items:
            pathname, desc = item
            title = desc.ljust(80, ' ')
            subtitle = ('%s ' % self.get_desc_type(pathname)) + pathname
            self.view_items.append([title, subtitle])

    def get_desc_type(self, pathname):
        if path.isdir(pathname): return 'DIR'

        basename = path.basename(pathname)
        name, ext = path.splitext(basename)
        return ext[1:].upper() or 'FILE'

    def show_quick_panel(self):
        self.window.show_quick_panel(self.view_items, self.on_done, on_highlight=self.on_highlight)

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
            if self.binfile_open_in_subl or not self.is_binary_file(filename):
                self.window.open_file(filename)
            else:
                self.open_binary_file(filename)

    def open_dir(self, dirname):
        if USER_PLATFORM == 'windows':
            subprocess.Popen(['explorer', dirname])
        elif USER_PLATFORM == 'osx':
            self.window.run_command('open_dir', { 'dir': dirname })

    def open_binary_file(self, filename):
        if USER_PLATFORM == 'windows':
            subprocess.Popen(['explorer', filename])
        elif USER_PLATFORM == 'osx':
            # TODO: add `open_binary_file` support for osx
            pass

        if self.peek_file: self.restore_view()

    def is_binary_file(self, filename):
        textchars = bytearray([7, 8, 9, 10, 12, 13, 27]) + bytearray(range(0x20, 0x100))
        leadbytes = open(filename, 'rb').read(1024)
        return bool(leadbytes.translate(None, textchars))

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
