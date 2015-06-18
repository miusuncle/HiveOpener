import sublime, sublime_plugin
from os import path

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class HiveOpenSwitcherCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        known_options = [
            'toggle_show_edit_item_option',
            'toggle_peek_file_on_highlight',
            'toggle_copy_url_on_open',
            'open_binary_file_in_sublime'
        ]

        self.options = sublime.load_settings(OPTIONS_BASE_NAME)

        for optname in args.keys():
            if optname not in known_options: continue

            if optname.startswith('toggle_'):
                optname = optname.replace('toggle_', '')
                optval = not self.options.get(optname)
            else:
                optval = args.get(optname)

            self.set_optval(optname, optval)

        sublime.save_settings(OPTIONS_BASE_NAME)

    def set_optval(self, optname, optval):
        self.options.set(optname, optval)
        sublime.status_message('`%s`\'s new value is: %s' % (optname, optval))
