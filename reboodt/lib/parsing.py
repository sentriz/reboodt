class IRCString:

    def __init__(self, raw_string):
    
        self.raw_string = raw_string

    def _parse_string(self, parse_for=None):

        parse_for = parse_for or self._get_string_type()

        to_parse = {
            'message': {
                'message':   lambda s: s.split(" :")[-1].replace("\r\n", ""),
                'sender':    lambda s: s[1:].split("!")[0],
                'target':    lambda s: s.split()[2]
            },
            'ping': {
                'pong':      lambda s: s.split()[1].rstrip()
            },
            'notice': {
                'message':   lambda s: " ".join(s.split()[3:])[1:]
            },
            'user_command': {
                'command':   lambda s: s.split(" :")[1].split()[0],
                'arguments': lambda s: s.split(" :")[1].split()[1:],
                'channel':   lambda s: s.split()[2],
                'sender':    lambda s: s[1:].split("!")[0]
            },
            'motd': {
                'message':   lambda s: " ".join(s.split()[3:])[1:]
            }
        }

        if parse_for in to_parse:
            to_return = {}
            for part, parse in to_parse[parse_for].items():
                to_return[part] = parse(self.raw_string)
            return to_return

    def _get_string_type(self):

        # not using dictionary because order is important here
        # "user_command" must always come before "message"
        types = (
            # (type to return, type finder, raw type comparison)
            ("ping", lambda s: s.split(" :")[0], "PING"),
            ("user_command", lambda s: s.split()[3][1], "."),
            ("message", lambda s: s.split()[1], "PRIVMSG"),
            ("motd", lambda s: s.split()[1], "372"),
            ("notice", lambda s: s.split()[1], "NOTICE")
        )

        for type_name, find_type, raw_type in types:
            try:
                result = find_type(self.raw_string)
            except IndexError:
                continue
            else:
                if result == raw_type:
                    return type_name
