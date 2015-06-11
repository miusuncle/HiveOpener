#HiveOpener

This is a Sublime Text 2/3 plugin to quickly open file/directory according to config file. Once you config your files/directories in the specified config file, you can then open your file in Sublime Text quickly, and open your directory in `Explorer(for windows)` or `Finder (for mac)` conveniently.

##Feature & Usage

### Add/remove file to/from open list

Right click the tab of the current opened file, then select `Add File to Open List` or `Remove File from Open List` command, your file will be registerred/unregisterred from the config file.

### Add/remove directory to/from open list

To add/remove directoy to/from open list, you need do it manually. Press `Alt+Shift+I` to open the config file, and add/remove your configuration to that file as formatted below:

For Windows:

```json
{
    "dirs": [
        ["C:\\Windows\\System32\\drivers\\etc", "windows_hosts_dir"]
    ],

    "files": [
        ["C:\\Windows\\System32\\drivers\\etc\\hosts", "windows_hosts_file"]
    ]
}
```

For Mac:

```json
{
    "dirs": [
        ["/etc", "osx_hosts_dir"]
    ],

    "files": [
        ["/etc/hosts", "osx_hosts_file"]
    ]
}
```

### Open file/directory from open list

Press `Alt+Shift+O`, the files/directories information you configured before will appear in drop down panel, select your choice, press `Enter` to open it. Enjoy!
