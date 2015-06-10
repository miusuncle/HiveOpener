import sublime, sublime_plugin
from os import path

SETTINGS_BASE_NAME = 'HiveOpener.sublime-settings'

class HiveAddToFavorCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings(SETTINGS_BASE_NAME)
        filename = self.get_file_name()
        index = self.index_in_list(filename, settings)

        if index == -1:
            self.add_to_list(settings)
        else:
            self.remove_from_list(index, settings)

    def is_visible(self):
        return bool(self.get_file_name())

    def description(self):
        filename = self.get_file_name()
        if not filename: return ''

        if self.index_in_list(filename) == -1:
            return 'Add to Open List'
        else:
            return 'Remove from Open List'

    def index_in_list(self, filename, settings=None):
        if settings == None:
            settings = sublime.load_settings(SETTINGS_BASE_NAME)

        file_list = [item[0] for item in settings.get('files', [])]
        return file_list.index(filename) if filename in file_list else -1

    def add_to_list(self, settings):
        file_list = settings.get('files', [])

        filename = self.get_file_name()
        basename = path.basename(filename)
        name, ext = path.splitext(basename)

        # check whether keep extention
        desc = name if ext in ['.exe', '.lnk', '.app'] else basename

        file_list.append([filename, desc])

        settings.set('files', file_list)
        sublime.save_settings(SETTINGS_BASE_NAME)

    def remove_from_list(self, index, settings):
        file_list = settings.get('files', [])
        file_list.pop(index)
        settings.set('files', file_list)
        sublime.save_settings(SETTINGS_BASE_NAME)

    def get_file_name(self):
        view = self.window.active_view()
        return (view.file_name() or '' if view else '')
