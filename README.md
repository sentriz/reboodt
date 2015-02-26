reebodt is a python **3+** [IRC bot](http://en.wikipedia.org/wiki/IRC_bot) that supports multiple servers, channels, and commands.

It also supports a "plugin" system to easily add your own commands and "variables" (explained below).

Installation
-----------
modify *files.config.py* to your liking, then

    python reboody.py

Commands
-----------
    ".calc 1 + 2" ... returns "3"
    ".qr string" ... returns "http://goo.gl/xxxxxx", a qr code of your string
    ".insult [user]" ... returns a shakespearean insult, optionally aimed at a user
    ".say string" ... return string, useful is string is a .variable
    ".join #channel"
    ".quit [message]" ... quit the current server with an optional message
    ".commands" ... show this list of commands

Variables
-----------
    ".time" ... returns "yyyy/mm/dd hh:mm:ss"
    ".last" ... returns the last message that was said