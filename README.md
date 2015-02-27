reboodt is a python **3+** [IRC bot](http://en.wikipedia.org/wiki/IRC_bot) that supports multiple servers, channels, and commands.

It also supports a "plugin" system to easily add your own commands and "variables" (explained below).

Installation
-----------
modify *files.config.py* to your liking, then

    python reboodt.py
	
Usage
-----------
- commands start with "." followed by the command name.. eg. ".calc"
- after the command, a string, variable, or a combination of the two can be passed as arguments
- an example of this would be ".qr .last", which would generate a QR code of that last message said in the channel
- the arguments don't have to be just a string or just a variable either, they can be mixed up
- eg. ".say the current time is .time on the server" hich would do exactly what you think


Commands
-----------
    ".calc 1 + 2" ... returns "3"
    ".qr string" ... returns "http://goo.gl/xxxxxx", a qr code of your string
    ".insult [user]" ... returns a shakespearean insult, optionally aimed at a user
    ".say string" ... returns "string", useful if string is a .variable
    ".join #channel" ... joins a #channel
    ".quit [message]" ... quit the current server with an optional message
    ".help [command]" ... display help for a command if provided. otherwise, list commands

Variables
-----------
    ".time" ... returns "yyyy/mm/dd hh:mm:ss"
    ".last" ... returns the last message that was said