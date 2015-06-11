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
            index = self.cmd2idx.get(cmd, -1)
            if index == -1: return
            action = self.action_list[index]

            if index < 3:
                self.show_input_panel(action)
            else:
                self.show_item_list(action)
        else:
            self.list_actions()

    def run_cmd(self):
        if self.hive_cmd.startswith('add_'):
            self.run()
        else:
            self.run(cmd=self.hive_cmd)

    def init(self): self.init_vars()

    def init_vars(self):
        self.cmd2idx = dict(
            add_dir  = 0, add_file  = 1, add_url  = 2,
            edit_dir = 3, edit_file = 4, edit_url = 5,
            del_dir  = 6, del_file  = 7, del_url  = 8
        )

        self.idx2cmd = dict((v, k) for k, v in self.cmd2idx.items())

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
                'input_checker': self.isurl,
                'save_to': 'urls'
            },

            {
                'name': 'Edit `DIR` from Open List',
                'onselect': 'show_item_list',
                'input_format': 'dirpath | description',
                'input_checker': path.isdir,
                'save_to': 'dirs',
                'command': 'edit'
            },
            {
                'name': 'Edit `FILE` from Open List',
                'onselect': 'show_item_list',
                'input_format': 'filepath | description',
                'input_checker': path.isfile,
                'save_to': 'files',
                'command': 'edit'
            },
            {
                'name': 'Edit `URL` from Open List',
                'onselect': 'show_item_list',
                'input_format': 'urlpath | description',
                'input_checker': self.isurl,
                'save_to': 'urls',
                'command': 'edit'
            },

            {
                'name': 'Delete `DIR` from Open List',
                'onselect': 'show_item_list',
                'save_to': 'dirs',
                'command': 'delete'
            },
            {
                'name': 'Delete `FILE` from Open List',
                'onselect': 'show_item_list',
                'save_to': 'files',
                'command': 'delete'
            },
            {
                'name': 'Delete `URL` from Open List',
                'onselect': 'show_item_list',
                'save_to': 'urls',
                'command': 'delete'
            }
        ]

    def list_actions(self):
        actions = [item['name'] for item in self.action_list]
        self.window.show_quick_panel(actions, self.on_select_action, sublime.MONOSPACE_FONT)

    def on_select_action(self, index):
        if index == -1: return
        item = self.action_list[index]
        getattr(self, item['onselect'])(item)
        self.hive_cmd = self.idx2cmd[index]

    def show_item_list(self, item):
        self.conf = sublime.load_settings(CONFIG_BASE_NAME)
        self.itemoption = item
        self.itemlist = self.conf.get(item['save_to'], [])

        showlist = [['Go Back', '>_ SHOW MAIN MENU']] + self.itemlist
        self.window.show_quick_panel(showlist, self.on_select_item)

    def on_select_item(self, index):
        if index in [-1, 0]: return self.run()
        self.hive_index = index - 1
        path, desc = self.itemlist[self.hive_index]

        if self.itemoption['command'] == 'edit':
            item = self.itemoption.copy()
            item.update(dict(init_text=' | '.join([path, desc])))
            self.show_input_panel(item)

        if self.itemoption['command'] == 'delete':
            self.itemlist.pop(self.hive_index)
            self.conf.set(self.itemoption['save_to'], self.itemlist)
            sublime.save_settings(CONFIG_BASE_NAME)
            sublime.status_message('Item `%s` has been deleted from open list.' % path)
            self.run_cmd()

    def show_input_panel(self, item):
        caption = '%s ( %s ):' % (item['name'], item['input_format'])
        init_text = item.get('init_text', '')
        checker, save_to = item['input_checker'], item['save_to']
        on_done = partial(self.on_input_info, checker, save_to)

        if gte_st3:
            self.window.show_input_panel(caption, init_text, on_done, None, on_cancel=self.run_cmd)
        else:
            self.window.show_input_panel(caption, init_text, on_done, None, self.run_cmd)

    def on_input_info(self, checker, save_to, input_text):
        path, desc = self.split_by_pipe(input_text)

        if checker is None or checker(path):
            conf = sublime.load_settings(CONFIG_BASE_NAME)
            dest = conf.get(save_to, [])
            index = self.index_in_list(path, dest)

            if self.hive_cmd.startswith('edit_'):
                dest[self.hive_index] = [path, desc]
            elif index == -1:
                dest.append([path, desc])
            else:
                dest[index] = [path, desc]

            conf.set(save_to, dest)
            sublime.save_settings(CONFIG_BASE_NAME)
            sublime.status_message('Item `%s` has been add to open list.' % path)

        else:
            sublime.status_message('Invalid input, action abort.')

        self.run_cmd()

    def index_in_list(self, needle, haystack):
        haystack = [item[0] for item in haystack]
        return haystack.index(needle) if needle in haystack else -1

    def split_by_pipe(self, text):
        if '|' not in text: text += '|'
        first, rest = text.strip().split('|', 1)
        return [first.strip(), rest.strip()]

    def isurl(self, url):
        return bool(REX_URL.match(url))

