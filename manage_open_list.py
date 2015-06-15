import sublime, sublime_plugin
from os import path

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class HiveManageOpenListCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        self.init_vars()

        if 'cmd' in args:
            cmd = args.get('cmd')
            index = self.index_from_command(cmd)

            if index != -1:
                self.on_select_action(index)
            else:
                sublime.status_message('Unknown command, action abort.')
        else:
            self.list_actions()

    def run_cmd(self):
        delay = 300 if self.hive_cmd.startswith('add_') else 10
        sublime.set_timeout(lambda: self.run(cmd=self.hive_cmd), delay)

    def init_vars(self):
        self.conf = sublime.load_settings(CONFIG_BASE_NAME)
        self.raw_items = self.get_raw_items()

        self.action_list = [
            {
                'command': 'add_item',
                'name': 'Add Item to Open List',
                'onselect': 'show_input_panel'
            },
            {
                'command': 'edit_item',
                'name': 'Edit Item from Open List',
                'onselect': 'show_item_list'
            },
            {
                'command': 'remove_item',
                'name': 'Remove Item from Open List',
                'onselect': 'show_item_list'
            }
        ]

        options = sublime.load_settings(OPTIONS_BASE_NAME)
        show_edit_item = options.get('show_edit_item_option', False)

        if not show_edit_item: self.action_list.pop(1)
        if not self.raw_items: self.action_list = self.action_list[0:1]

    def list_actions(self):
        actions = [item['name'] for item in self.action_list]
        self.window.show_quick_panel(actions, self.on_select_action)

    def on_select_action(self, index):
        if index == -1: return

        self.hive_action = self.action_list[index]
        self.hive_cmd = self.hive_action['command']

        getattr(self, self.hive_action['onselect'])()

    def index_from_command(self, command):
        for (index, action) in enumerate(self.action_list):
            if command == action['command']:
                return index
        else: return -1

    def show_item_list(self):
        view_items = self.build_view_items()
        down_arrows = u'\u2193 ' * 3

        if self.hive_cmd == 'edit_item':
            first_item = [u'\u2190 Back', down_arrows + u'Edit Item(s) Below ' + down_arrows]

        if self.hive_cmd == 'remove_item':
            first_item = [u'\u2190 Back', down_arrows + u'Remove Item(s) Below ' + down_arrows]

        view_items = [first_item] + view_items

        self.window.show_quick_panel(view_items, self.on_select_item)

    def get_raw_items(self):
        result = []

        for key in DEFAULT_ITEM_TYPES:
            if not self.conf.has(key): continue
            result.extend(self.conf.get(key))

        # sort items alphabetically
        result.sort(key=lambda x: x[1].lower())
        return result

    def build_view_items(self):
        result = []

        for (pathname, desc) in self.raw_items:
            title = desc

            if not title:
                if self.isfile(pathname):
                    title = path.basename(pathname) or pathname
                else:
                    title = pathname

            subtitle = '%s %s' % (self.get_item_type(pathname), pathname)
            result.append([title, subtitle])

        return result

    def on_select_item(self, index):
        # triggered `escape` or `back`
        if index in [-1, 0]: return self.run()
        currpath, currdesc = self.raw_items[index - 1]

        self.hive_raw_path = currpath
        self.hive_raw_type = self.get_item_raw_type(currpath)
        dest = self.conf.get(self.hive_raw_type, [])
        self.hive_raw_index = self.index_in_list(currpath, dest)

        if self.hive_cmd == 'edit_item':
            self.show_input_panel(dict(path=currpath, desc=currdesc))

        if self.hive_cmd == 'remove_item':
            dest.pop(self.hive_raw_index)

            self.conf.set(self.hive_raw_type, dest)
            sublime.save_settings(CONFIG_BASE_NAME)

            sublime.status_message('Item `%s` has been deleted from open list.' % currpath)
            self.run_cmd() if self.get_raw_items() else self.run()

    def show_input_panel(self, itemdata=None):
        caption = '%s ( %s ):' % (self.hive_action['name'], 'path | description')

        if itemdata is None:
            init_text = ''
        else:
            if itemdata['desc']:
                init_text = '%s | %s' % (itemdata['path'], itemdata['desc'])
            else:
                init_text = itemdata['path']

        on_done = self.on_input_info
        on_cancel = self.run if self.hive_cmd.startswith('add_') else self.run_cmd

        if gte_st3:
            self.window.show_input_panel(caption, init_text, on_done, None, on_cancel=on_cancel)
        else:
            self.window.show_input_panel(caption, init_text, on_done, None, on_cancel)

    def on_input_info(self, input_text):
        path, desc = self.split_via_pipe(input_text)

        if self.isurl(path): save_to = 'urls'
        elif self.isfile(path): save_to = 'files'
        elif self.isdir(path): save_to = 'dirs'
        else: save_to = None

        if save_to is None:
            sublime.status_message('Invalid input, action abort.')
            self.run_cmd()
        else:
            if self.hive_cmd == 'edit_item':
                dest = self.conf.get(self.hive_raw_type, [])
                # remove it first
                dest.pop(self.hive_raw_index)
                self.conf.set(self.hive_raw_type, dest)

            dest = self.conf.get(save_to, [])
            index = self.index_in_list(path, dest)
            item = [path, desc]

            if self.hive_cmd == 'edit_item' and save_to == self.hive_raw_type:
                if index == -1:
                    dest.insert(self.hive_raw_index, item)
                else:
                    dest[index] = item

            elif index == -1:
                dest.append(item)
            else:
                dest[index] = item

            self.conf.set(save_to, dest)
            sublime.save_settings(CONFIG_BASE_NAME)
            sublime.status_message('Item `%s` has been added to open list.' % path)

            self.run_cmd() if self.hive_cmd == 'edit_item' else self.run()

    def get_item_raw_type(self, pathname):
        if self.isurl(pathname): return 'urls'
        if self.isfile(pathname): return 'files'
        if self.isdir(pathname): return 'dirs'

    def get_item_type(self, pathname):
        if self.isurl(pathname): return 'URL'

        if self.isfile(pathname):
            name, ext = path.splitext(pathname)
            return ext[1:].upper() or 'FILE'

        if self.isdir(pathname): return 'DIR'
        return 'UNKNOWN'

    def index_in_list(self, needle, haystack):
        haystack = [item[0] for item in haystack]
        return haystack.index(needle) if needle in haystack else -1

    def split_via_pipe(self, text):
        if '|' not in text: text += '|'
        first, rest = text.strip().split('|', 1)

        # do some favor on windows, replace double backslashes with single ones
        first = first.replace(r'\\', '\\')

        return [first.strip('"\' '), rest.strip('"\' ')]

    def isurl(self, target): return bool(REX_URL.match(target))

    def isfile(self, target):
        name, ext = path.splitext(target)

        if SUBLIME_PLATFORM == 'osx' and ext == '.app':
            return True

        return path.isfile(target)

    def isdir(self, target): return path.isdir(target)
