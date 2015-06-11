import sublime, sublime_plugin
from os import path

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class HiveOpenSwitcherCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        if 'toggle_peek_file_on_highlight' in args:
            self.toggle_peek_file()

        if 'open_binary_file_in_sublime' in args:
            binfile_open_in_subl = args.get('open_binary_file_in_sublime')
            self.set_open_binary_file(binfile_open_in_subl)

    def toggle_peek_file(self):
        options = sublime.load_settings(OPTIONS_BASE_NAME)
        peek_file = not options.get('peek_file_on_highlight', False)
        options.set('peek_file_on_highlight', peek_file)
        sublime.save_settings(OPTIONS_BASE_NAME)

    def set_open_binary_file(self, value):
        options = sublime.load_settings(OPTIONS_BASE_NAME)
        options.set('open_binary_file_in_sublime', value)
        sublime.save_settings(OPTIONS_BASE_NAME)
