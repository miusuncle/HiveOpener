import sublime, sublime_plugin
import re

rex = re.compile(
    r'''(?x)
    \b(?:
        https?://(?:(?:[a-zA-Z0-9\-_]+(?:\.[a-zA-Z0-9\-._]+)+)|localhost)|  # http://
        www\.[a-zA-Z0-9\-_]+(?:\.[a-zA-Z0-9\-._]+)+                         # www.
    )
    /?[a-zA-Z0-9\-._?,!'(){}\[\]/+&@%$#=:"|~;]*                             # url path and query string
    [a-zA-Z0-9\-_~:/#@$*+=]                                                 # allowed end chars
    ''')

gte_st3 = int(sublime.version()) >= 3000

if gte_st3:
    from .config import *
else:
    from config import *

class AddContextUrlBaseCommand(sublime_plugin.TextCommand):
    def run(self, edit, event=None):
        conf = sublime.load_settings(CONFIG_BASE_NAME)
        url = self.find_url(event)
        index = self.index_in_list(url, conf)

        if index == -1:
            self.add_to_list(url, conf)
        else:
            self.remove_from_list(index, conf)

    def is_visible(self, event=None):
        return self.find_url(event) is not None

    def description(self, event=None):
        url = self.find_url(event)

        if self.index_in_list(url) == -1:
            return 'Add URL to Open List'
        else:
            return 'Remove URL from Open List'

    def index_in_list(self, url, conf=None):
        if conf == None:
            conf = sublime.load_settings(CONFIG_BASE_NAME)

        url_list = [item[0] for item in conf.get('urls', [])]
        return url_list.index(url) if url in url_list else -1

    def add_to_list(self, url, conf):
        url_list = conf.get('urls', [])
        url_list.append([url, ''])
        conf.set('urls', url_list)
        sublime.save_settings(CONFIG_BASE_NAME)

    def remove_from_list(self, index, conf):
        url_list = conf.get('urls', [])
        url_list.pop(index)
        conf.set('urls', url_list)
        sublime.save_settings(CONFIG_BASE_NAME)

    def find_url(self, pt):
        line = self.view.line(pt)
        a, b = [max(line.a, pt - 1024), min(line.b, pt + 1024)]
        line = sublime.Region(a, b)

        text = self.view.substr(line)

        it = rex.finditer(text)

        for match in it:
            if match.start() <= (pt - line.a) and match.end() >= (pt - line.a):
                url = text[match.start():match.end()]
                return url

        return None

if gte_st3:

    class AddContextUrlCommand(AddContextUrlBaseCommand):
        def find_url(self, event):
            pt = self.view.window_to_text((event['x'], event['y']))
            return super(AddContextUrlCommand, self).find_url(pt)

        def want_event(self):
            return True
else:

    class AddContextUrlCommand(AddContextUrlBaseCommand):
        def find_url(self, event):
            selection = self.view.sel()
            if not len(selection): return None

            pt = selection[-1].b
            return super(AddContextUrlCommand, self).find_url(pt)
