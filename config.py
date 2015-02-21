admins = ["sentriz", "sentriz_android"]
command_prefix = "."

# add as many as you can handle
servers = [
    {
        'connect':  True,
        'name':     "GeekShed",
        'host':     "irc.geekshed.net",
        'port':     6667,
        'nick':     "reboodt",
        'chans':    ["#drpeen", "#testong"],
        'auth':     (False, "password") #authenticate with NickServ? if True, type password too.
    },
    {
        'connect':  False,
        'name':     "EsperNet",
        'host':     "irc.esper.net",
        'port':     6667,
        'nick':     "rebooped",
        'chans':    ["#tests"],
        'auth':     (False, "password")
    },
    {
        'connect':  False,
        'name':     "ExampleNet",
        'host':     "irc.example.net",
        'port':     6667,
        'nick':     "bot_nick",
        'chans':    ["#channel1", "channel2"],
        'auth':     (False, "password")
    }
]