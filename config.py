import sublime
import re

SUBLIME_PLATFORM = sublime.platform()
OPTIONS_BASE_NAME = 'HiveOpenerOptions.sublime-settings'
CONFIG_BASE_NAME = 'HiveOpenerConfig.sublime-settings'

REX_URL = re.compile(
    r'''(?x)
    \b(?:
        https?://(?:(?:[a-zA-Z0-9\-_]+(?:\.[a-zA-Z0-9\-._]+)+)|localhost)|  # http://
        www\.[a-zA-Z0-9\-_]+(?:\.[a-zA-Z0-9\-._]+)+                         # www.
    )
    /?[a-zA-Z0-9\-._?,!'(){}\[\]/+&@%$#=:"|~;]*                             # url path and query string
    [a-zA-Z0-9\-_~:/#@$*+=]                                                 # allowed end chars
    ''')

REX_QUOTES = re.compile(r'"(.+)"')
