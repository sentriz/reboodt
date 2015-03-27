**reboodt** is a python *3+* [IRC bot](http://en.wikipedia.org/wiki/IRC_bot) that supports multiple servers, channels, and commands.  
It also supports a modular **plugin** system to easily add your *own* commands and variables. (explained below)  
###### note: this software has only been tested on Python 3.4.0, please report any issues you may have on earlier Python 3 versions


home: [sentriz.github.io/reboodt](http://sentriz.github.io/reboodt)  
github: [github.com/sentriz/reboodt](https://github.com/sentriz/reboodt)

Installation
-----------
move `config.sample.yml` to `config.yml` and modify.  
move `api_keys.sample.yml` to `api_keys.yml` and (optionally) modify.  

    python reboodt.py
    
Usage
-----------
- commands start with `.` followed by the command name ..
  - eg. `.calc` ..
- after the command - a string or variable can be passed as an argument ..
  - eg. `.qr .last`, which would generate a [QR code](http://en.wikipedia.org/wiki/QR_code) of the last message said in the channel ..
- the arguments don't have to be just a string or just a variable either, they can be mixed up ..
  - eg. `.say the current time is .time on the server` ..
- to create a command/variable ..
  - make a copy of `files/template.txt` for dir `plugins/` ..
  - rename to `your_plugin.py` ..
  - modify ..

Commands
-----------

note: `[]` denotes optional arguments

command..   | takes argument(s).. | and returns..
------------|---------------------|--------------
**.8**      | `question`          | a positive, negative, or neutral [magic 8 ball](http://en.wikipedia.org/wiki/Magic_8-Ball) reply
**.calc**   | `expression`        | an evaluation of a mathematical `expression` (eg `.calc 1 + 2` returns `3`)
**.define** | `word`              | a definition of a `word`
**.fmnp**   | `user`              | what a [last.fm](http://last.fm/) `user` is, or was, listening to 
**.fmu**    | `user`              | info on a [last.fm](http://last.fm/) `user`
**.google** | `query`             | top 4 Google results when searching for a `query`
**.help**   | `[command]`         | help for a `command` if provided. otherwise, a list commands
**.insult** | `[user]`            | a shakespearean insult, optionally aimed at a `user`
**.join**   | `#channel`          | 
**.py**     | `expression`        | a python `expression` evaluated (eg. `.py len([1, 2])` returns `2`)
**.qr**     | `string`            | a qr code of your `string`
**.quit**   | `[message]`         | 
**.reload** |                     | nothing; command reloads all plugins in the `plugin/` directory
**.say**    | `string`            | `string`, useful if `string` has a `.variable`

Variables
-----------

variable  | is replaced with..
----------|-------------------
**.last** | the `last` message that was said in the channel
**.time** | "yyyy/mm/dd hh:mm:ss"
