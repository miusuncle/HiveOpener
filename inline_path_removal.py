import sublime, sublime_plugin
from os import path

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class HiveInlinePathRemovalBaseCommand(sublime_plugin.TextCommand):
    def run(self, edit, event=None):
        conf = sublime.load_settings(CONFIG_BASE_NAME)
        quoted_str = self.find_quoted_str(event)
        index = self.index_in_list(quoted_str, conf)
        self.remove_from_list(index, conf)

        if isfile(quoted_str):
            sublime.status_message('File `%s` has been removed from open list.' % quoted_str)
        else:
            sublime.status_message('Dir `%s` has been removed from open list.' % quoted_str)

    def is_visible(self, event=None):
        filename = self.view.file_name() or ''
        basename = path.basename(filename)
        if basename != CONFIG_BASE_NAME: return False

        quoted_str = self.find_quoted_str(event)
        if quoted_str is None: return False

        if isfile(quoted_str) or isdir(quoted_str):
            return self.index_in_list(quoted_str) != -1
        else:
            return False

    def description(self, event=None):
        quoted_str = self.find_quoted_str(event)

        if isfile(quoted_str):
            return 'Remove File from Open List'
        else:
            return 'Remove Dir from Open List'

    def index_in_list(self, quoted_str, conf=None):
        if conf == None:
            conf = sublime.load_settings(CONFIG_BASE_NAME)

        quoted_str = quoted_str.replace(r'\\', '\\')
        self.key = 'files' if isfile(quoted_str) else 'dirs'
        items = [item[0] for item in conf.get(self.key, [])]

        return items.index(quoted_str) if quoted_str in items else -1

    def remove_from_list(self, index, conf):
        items = conf.get(self.key, [])
        items.pop(index)
        conf.set(self.key, items)
        sublime.save_settings(CONFIG_BASE_NAME)

    def find_quoted_str(self, pt):
        line = self.view.line(pt)
        a, b = [max(line.a, pt - 1024), min(line.b, pt + 1024)]
        line = sublime.Region(a, b)

        text = self.view.substr(line).strip()

        it = REX_QUOTES.finditer(text)

        for match in it:
            if match.start() <= (pt - line.a) and match.end() >= (pt - line.a):
                quoted_str = text[match.start():match.end()]
                return quoted_str.strip('"')

        return None


if gte_st3:

    class HiveInlinePathRemovalCommand(HiveInlinePathRemovalBaseCommand):
        def find_quoted_str(self, event):
            pt = self.view.window_to_text((event['x'], event['y']))
            return super(HiveInlinePathRemovalCommand, self).find_quoted_str(pt)

        def want_event(self):
            return True
else:

    class HiveInlinePathRemovalCommand(HiveInlinePathRemovalBaseCommand):
        def find_quoted_str(self, event):
            selection = self.view.sel()
            if not len(selection): return None

            pt = selection[-1].b
            return super(HiveInlinePathRemovalCommand, self).find_quoted_str(pt)

def isfile(target):
    name, ext = path.splitext(target or '')
    if SUBLIME_PLATFORM == 'osx' and ext == '.app':
        return True

    return path.isfile(target)

def isdir(target): return path.isdir(target or '')
