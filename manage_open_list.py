import sublime, sublime_plugin
from os import path
from functools import partial

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class HiveManageOpenListCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        self.init()

        if 'cmd' in args:
            cmd = args.get('cmd')
            action = self.action_list[self.cmds[cmd]]
            self.show_input_panel(action)
        else:
            self.list_actions()

    def init(self):
        self.init_vars()

    def init_vars(self):
        self.cmds = dict(add_dir=0, add_file=1, add_url=2)

        self.action_list = [
            {
                'name': 'Add `DIR` to Open List',
                'onselect': 'show_input_panel',
                'input_format': 'dirpath | description',
                'input_checker': path.isdir,
                'save_to': 'dirs'
            },
            {
                'name': 'Add `FILE` to Open List',
                'onselect': 'show_input_panel',
                'input_format': 'filepath | description',
                'input_checker': path.isfile,
                'save_to': 'files'
            },
            {
                'name': 'Add `URL` to Open List',
                'onselect': 'show_input_panel',
                'input_format': 'urlpath | description',
                'input_checker': None,
                'save_to': 'urls'
            }
        ]

    def list_actions(self):
        actions = [item['name'] for item in self.action_list]
        self.window.show_quick_panel(actions, self.on_select_action, sublime.MONOSPACE_FONT)

    def on_select_action(self, index):
        if index == -1: return
        item = self.action_list[index]
        getattr(self, item['onselect'])(item)

    def show_input_panel(self, item):
        caption = '%s ( %s ):' % (item['name'], item['input_format'])

        checker, save_to = item['input_checker'], item['save_to']
        on_done = partial(self.on_input_info, checker, save_to)

        if gte_st3:
            self.window.show_input_panel(caption, '', on_done, None, on_cancel=None)
        else:
            self.window.show_input_panel(caption, '', on_done, None, None)

    def on_input_info(self, checker, save_to, input_text):
        path, desc = self.split_by_pipe(input_text)

        if checker is None or checker(path):
            conf = sublime.load_settings(CONFIG_BASE_NAME)
            dest = conf.get(save_to, [])
            index = self.index_in_list(path, dest)

            if index == -1:
                dest.append([path, desc])
            else:
                dest[index] = [path, desc]

            conf.set(save_to, dest)
            sublime.save_settings(CONFIG_BASE_NAME)
            sublime.status_message('Item %s has been add to open list.' % path)

        else:
            sublime.status_message('Invalid input, action abort.')

    def index_in_list(self, needle, haystack):
        haystack = [item[0] for item in haystack]
        return haystack.index(needle) if needle in haystack else -1

    def split_by_pipe(self, text):
        if '|' not in text: text += '|'
        first, rest = text.strip().split('|', 1)
        return [first.strip(), rest.strip()]
