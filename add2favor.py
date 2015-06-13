import sublime, sublime_plugin
from os import path

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class HiveAddToFavorCommand(sublime_plugin.WindowCommand):
    def run(self):
        filename = self.get_file_name()
        conf = sublime.load_settings(CONFIG_BASE_NAME)
        index = self.index_in_list(filename, conf)

        if index == -1:
            self.add_to_list(filename, conf)
            sublime.status_message('File `%s` has been added to open list.' % filename)
        else:
            self.remove_from_list(index, conf)
            sublime.status_message('File `%s` has been removed from open list.' % filename)

    def is_visible(self):
        return bool(self.get_file_name())

    def description(self):
        filename = self.get_file_name()
        if not filename: return ''

        if self.index_in_list(filename) == -1:
            return 'Add File to Open List'
        else:
            return 'Remove File from Open List'

    def index_in_list(self, filename, conf=None):
        if conf == None:
            conf = sublime.load_settings(CONFIG_BASE_NAME)

        file_list = [item[0] for item in conf.get('files', [])]
        return file_list.index(filename) if filename in file_list else -1

    def add_to_list(self, filename, conf):
        file_list = conf.get('files', [])

        basename = path.basename(filename)
        name, ext = path.splitext(basename)

        # check whether keep extention
        desc = name if ext in ['.exe', '.lnk', '.app'] else basename

        file_list.append([filename, desc])

        conf.set('files', file_list)
        sublime.save_settings(CONFIG_BASE_NAME)

    def remove_from_list(self, index, conf):
        file_list = conf.get('files', [])
        file_list.pop(index)
        conf.set('files', file_list)
        sublime.save_settings(CONFIG_BASE_NAME)

    def get_file_name(self):
        view = self.window.active_view()
        return (view.file_name() or '' if view else '')
