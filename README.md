**reboodt** is a python *3+* [IRC bot](http://en.wikipedia.org/wiki/IRC_bot) that supports multiple servers, channels, and commands.  
It also supports a modular **plugin** system to easily add your *own* commands and variables. (explained below)
home: [sentriz.github.io/reboodt](http://sentriz.github.io/reboodt)

Installation
-----------
modify `config.py` to your liking, then

    python reboodt.py
    
Usage
-----------
- commands start with `.` followed by the command name - eg. `.calc`
- after the command - a string, variable, or a combination of the two can be passed as arguments
  - an example of this would be `.qr .last`, which would generate a QR code of that last message said in the channel
- the arguments don't have to be just a string or just a variable either, they can be mixed up
  - eg. `.say the current time is .time on the server` which would do exactly what you think
- to create a command/variable - make a copy of `files/template.txt` for dir `plugins/`, rename to `plugin.py`, and modify


Commands
-----------
note: `[]` denotes optional arguments

    ".calc 1 + 2"       ... returns "3"
    ".google query"     ... search google for a query
    ".help [command]"   ... returns help for a command if provided. otherwise, list commands
    ".insult [user]"    ... returns a shakespearean insult, optionally aimed at a user
    ".join #channel"    ... joins a #channel
    ".py expression"    ... evaluate a python expression, eg. "len([1, 2])" returns "2"
    ".qr string"        ... returns "http://goo.gl/xxxxxx", a qr code of your string
    ".quit [message]"   ... quit the current server with an optional message
    ".reload"           ... reload all plugins in the plugins directory
    ".say string"       ... returns "string", useful if string is a .variable

Variables
-----------

    ".last"           ... returns the last message that was said
    ".time"           ... returns "yyyy/mm/dd hh:mm:ss"
	