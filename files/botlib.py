# Based on Alec Hussey's PyBotlib

import socket
from collections import OrderedDict
import sys
import time
import random
import string
import threading
import files.config as config

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
            chunk = self.connection.recv(512).decode()
            if not chunk:
                raise RuntimeError("Connection reset by peer.")
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

class Bot(threading.Thread):
    def __init__(self, server, port, channels, nick, network_name, authentication):
        # intialize threading
        threading.Thread.__init__(self)

        # initialize IRC protocol
        self.protocol = Protocol(server, port)
        self.protocol.identify(nick)

        # initialize class variables
        self.server = server
        self.port = port
        self.channels = channels
        self.nick = nick
        self.data = None
        self.last_message = None
        self.joined = False
        self.network_name = network_name
        self.authentication = authentication

    def _actions(self):
        """
        loop that listens and performs defined commands
        """
        # recieve incoming data from server
        self.data = self.protocol.recv()
        string_type = self.get_string_type()

        # Check for and respond to PING requests
        if string_type == "PING":
            pong = self.parse_string()["pong"]
            self.protocol.send("PONG " + pong)

            # check to see if the client has joined their
            # specified channels yet, if not join it
            if not self.joined:
                for channel in self.channels:
                    self.protocol.join(channel)
                self.joined = True

        elif string_type in ("PRIVMSG", "command"):
            parsed_string = self.parse_string("PRIVMSG")
            print("[{0}][{1}] <{2}> {3}".format(
                self.network_name,
                parsed_string["target"],
                parsed_string["sender"],
                parsed_string["message"]
            ))
            if string_type == "PRIVMSG":
                non_command_message = parsed_string["message"]
                self.last_message = non_command_message

        elif string_type == "NOTICE":
            auth_or_not, password = self.authentication
            if not auth_or_not:
                return
            # This nickname is registered.. please choose..
            if not "choose a different" in self.data:
                return
            self.protocol.privmsg("NickServ", "identify " + password)

    def parse_string(self, to_get=None, string=None):

        if not string:
            string = self.data

        if not to_get:
            to_get = self.get_string_type(string)

        to_parse = {
            'PRIVMSG': {
                'message':   lambda s: s.split(" :")[-1].replace("\r\n", ""),
                'sender':    lambda s: s[1:].split("!")[0],
                'target':    lambda s: s.split()[2]
            },
            'PING': {
                'pong':      lambda s: s.split()[1].rstrip()
            },
            'NOTICE': {
                'message':   lambda s: " ".join(s.split()[3:])[1:]
            },
            'command': {
                'command':   lambda s: s.split(" :")[1].split()[0],
                'arguments': lambda s: s.split(" :")[1].split()[1:],
                'channel':   lambda s: s.split()[2],
                'sender':    lambda s: s[1:].split("!")[0]
            },
            'motd': {
                'message':   lambda s: " ".join(s.split()[3:])[1:]
            }
        }

        if to_get in to_parse:
            to_return = {}
            for part, parse in to_parse[to_get].items():
                try:
                    to_return[part] = parse(string)
                except KeyError:
                    return None
            return to_return

    def get_string_type(self, string=None):

        if not string:
            string = self.data

        types = OrderedDict([
            ("PING",     (lambda s: s.split(" :")[0], "PING")),
            ("command",  (lambda s: s.split()[3][1], ".")),
            ("PRIVMSG",  (lambda s: s.split()[1], "PRIVMSG")),
            ("motd",     (lambda s: s.split()[1], "372")),
            ("NOTICE",   (lambda s: s.split()[1], "NOTICE"))
        ])

        for type, (find_type, correct_type) in types.items():
            try:
                result = find_type(string)
            except IndexError:
                continue
            else:
                if result == correct_type:
                    return type

    def say(self, message, channel=None):
        if not channel:
            parsed_string = self.parse_string("PRIVMSG")
            channel = parsed_string["target"]

        self.protocol.privmsg(channel, message)
        print("[{0}][{1}] <{2}> {3}".format(
            self.network_name,
            channel,
            self.nick,
            message
        ))
        self.last_message = message

    def run(self):
        # start loop and perform user defined actions
        while True:
            self._actions()
