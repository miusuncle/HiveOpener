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

SETTINGS_BASE_NAME = 'HiveOpener.sublime-settings'

class AddContextUrlCommand(sublime_plugin.TextCommand):
    def run(self, edit, event):
        settings = sublime.load_settings(SETTINGS_BASE_NAME)
        url = self.find_url(event)
        index = self.index_in_list(url, settings)

        if index == -1:
            self.add_to_list(url, settings)
        else:
            self.remove_from_list(index, settings)

    def is_visible(self, event):
        return self.find_url(event) is not None

    def description(self, event):
        url = self.find_url(event)

        if self.index_in_list(url) == -1:
            return 'Add URL to Open List'
        else:
            return 'Remove URL from Open List'

    def index_in_list(self, url, settings=None):
        if settings == None:
            settings = sublime.load_settings(SETTINGS_BASE_NAME)

        url_list = [item[0] for item in settings.get('urls', [])]
        return url_list.index(url) if url in url_list else -1

    def add_to_list(self, url, settings):
        url_list = settings.get('urls', [])
        url_list.append([url, ''])
        settings.set('urls', url_list)
        sublime.save_settings(SETTINGS_BASE_NAME)

    def remove_from_list(self, index, settings):
        url_list = settings.get('urls', [])
        url_list.pop(index)
        settings.set('urls', url_list)
        sublime.save_settings(SETTINGS_BASE_NAME)

    def find_url(self, event):
        pt = self.view.window_to_text((event['x'], event['y']))
        line = self.view.line(pt)

        line.a = max(line.a, pt - 1024)
        line.b = min(line.b, pt + 1024)

        text = self.view.substr(line)

        it = rex.finditer(text)

        for match in it:
            if match.start() <= (pt - line.a) and match.end() >= (pt - line.a):
                url = text[match.start():match.end()]
                if url[0:3] == 'www':
                    return 'http://' + url
                else:
                    return url

        return None

    def want_event(self):
        return True