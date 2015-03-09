# Based on Alec Hussey's PyBotlib

import socket
import sys
import time
import random
import string

class Protocol:
    def __init__(self, server, port=6667):
        self.connection = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.connection.connect((server, port))

    def send(self, message):
        """
        send chunks of the message until the entire
        message has been sent to the server
        """
        
        datasent = 0
        message += "\n"

        while datasent < len(message):
            sent = self.connection.send(message.encode())
            if sent == 0:
                raise RuntimeError("Connection reset by peer.")
            else:
                datasent += sent

    def recv(self):
        """
        recieve data from the server until
        we have recieved the end of the message
        """
        
        data = ""
        
        while "\r" not in data:
            try:
                chunk = self.connection.recv(512).decode()
            except TimeoutError:
                raise RuntimeError("connection timed out")
            if not chunk:
                raise RuntimeError("connection reset by peer")
            else:
                data += chunk

        return data

    def join(self, channel):
        self.send("JOIN " + channel)

    def notice(self, nickname, text):
        self.send("NOTICE {0} :{1}".format(nickname, text))

    def privmsg(self, reciever, message):
        self.send("PRIVMSG {0} :{1}".format(reciever, message))

    def topic(self, channel, topic):
        self.send("TOPIC {0} :{1}".format(channel, topic))

    def identify(self, username):
        self.send("USER {0} localhost localhost :{1}".format(
            username, username))
        self.send("NICK " + username)

    def whois(self, nickname):
        """
        pull whois data from server
        """
        
        self.send("WHOIS " + nickname)

        data = ""
        while "End of WHOIS" not in data:
            data += self.recv()
        return data

    def disconnect(self, message="disconnect"):
        self.send("QUIT :" + message)
        #time.sleep(5.0)
        #self.connection.shutdown(socket.SHUT_RDWR)
        #self.connection.close()

class Bot():
    def __init__(self, server, port, channels, nick, network_name, authentication):
        # initialise IRC protocol
        self.protocol = Protocol(server, port)
        self.protocol.identify(nick)

        # initialise class variables
        self.server = server
        self.port = port
        self.channels = channels
        self.nick = nick
        
        self.in_channels = False
        self.network_name = network_name
        self.authentication = authentication
        
        # initialise raw / command type / channel strings
        self.data = ""
        self.last_command_type = ""
        self.last_command_parsed = {}
        self.last_channel_message = ""

    def _actions(self):
        """
        loop that listens and performs defined commands
        """

        # check for and respond to PING requests
        if self.last_command_type == "ping":
            pong = self.last_command_parsed["pong"]
            self.protocol.send("PONG " + pong)
            
            if not self.in_channels:
                self._join_channels()
                self.in_channels = True

        elif self.last_command_type in ("message", "user_command"):
            # force "message" in case last_command_type is "command"
            parsed_command = self._parse_raw_command(parse_for="message")
            
            # ignore possibly junky startup messages
            if not parsed_command["target"].startswith("#"):
                return
                
            self.cprint("[{0}] <{1}> {2}".format(
                parsed_command["target"],
                parsed_command["sender"],
                parsed_command["message"]
            ))
            
            # add the message to self.last_channel_message, 
            # but not if it was a command
            if not self.last_command_type == "user_command":
                self.last_channel_message = parsed_command["message"]

        elif self.last_command_type == "notice":
            auth_or_not, password = self.authentication
            
            if not auth_or_not:
                return

            # hook NickServ asking for authentication
            # "this nickname is registered".. "please choose"..
            if not "choose a different" in self.data:
                return
            self.protocol.privmsg("NickServ", "identify " + password)
            hidden_password = "*"*len(password)
            
            self.cprint("identifed with NickServ with pass", hidden_password)
            
    def _join_channels(self):

        for channel in self.channels:
            if not channel.startswith("#"):
                continue
            self.protocol.join(channel)
            self.cprint('joined channel "{0}"'.format(channel))

    def _parse_raw_command(self, parse_for=None, raw_command=None):

        raw_command = raw_command or self.data
        parse_for = parse_for or self._get_raw_command_type(raw_command)

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
                to_return[part] = parse(raw_command)
            return to_return

    def _get_raw_command_type(self, raw_command=None):
    
        raw_command = raw_command or self.data
        
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
                result = find_type(raw_command)
            except IndexError:
                continue
            else:
                if result == raw_type:
                    return type_name

    def say(self, message, channel=None):
    
        if not channel:
            parsed_string = self._parse_raw_command(parse_for="message")
            channel = parsed_string["target"]

        self.protocol.privmsg(channel, message)
        self.cprint("[{0}] <{1}> {2}".format(
            channel,
            self.nick,
            message
        ))
        self.last_channel_message = message
    
    def cprint(self, *message):
        full_message = " ".join(message)
        print("{0}: {1}".format(self.network_name, full_message))

    def run(self):
        """
        main bot run method, loops and parses IRC commands
        """  
        
        # listen
        while True:
            # receive incoming data from server
            try:
                self.data = self.protocol.recv()
            except RuntimeError as error:
                self.cprint("error: " + error)
                sys.exit(1)
            
            # PRIVMSG, NOTICE, ect.
            self.last_command_type = self._get_raw_command_type()
            self.last_command_parsed = self._parse_raw_command(
                self.last_command_type)
                
            # perform basic actions like pong, ect.
            self._actions()
