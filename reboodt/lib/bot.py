# Based on Alec Hussey's PyBotlib

import config
import imp
import logging
import os
import socket
import sys
import time

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
        # time.sleep(5.0)
        # self.connection.shutdown(socket.SHUT_RDWR)
        # self.connection.close()

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
class Bot():
    def __init__(self, server, port, channels, 
            nick, network_name, authentication):
            
        logging.info('initialising "{0}" bot'.format(network_name))
    
        # initialise IRC protocol
        self.protocol = Protocol(server, port)
        self.protocol.identify(nick)

        # initialise class variables
        self.server = server
        self.port = port
        self.channels = channels
        self.nick = nick
        self.network_name = network_name
        self.authentication = authentication
        
        # misc booleans
        self.in_channels = False
        
        # plugin/help data/method calls 
        self.commands = {}
        self.variables = {}
        self.help = {}
        
        self.load_plugins()
        self.load_help()

        # initialise raw/command-type/channel strings
        self.raw_string = ""
        self.last_string_type = ""
        self.last_string_parsed = {}
        self.last_channel_message = ""
        
    def _actions(self):
        """
        loop that listens and performs defined commands
        """

        # check for and respond to PING requests
        if self.last_string_type == "ping":
            pong = self.last_string_parsed["pong"]
            self.protocol.send("PONG " + pong)
            
            if not self.in_channels:
                self._join_channels()
                self.in_channels = True

        elif self.last_string_type == "notice":
            auth_or_not, password = self.authentication
            
            if not auth_or_not:
                return

            # hook NickServ asking for authentication
            # "this nickname is registered".. "please choose"..
            if "choose a different" in self.raw_string:
                self.protocol.privmsg("NickServ", "identify " + password)
                hidden_password = "*"*len(password)
                logging.info("identifed with NickServ with pass " + hidden_password)
        
        elif self.last_string_type == "message":
            
            # ignore junky startup messages by ensuring
            # - channel starts with "#"
            if not self.last_string_parsed["target"].startswith("#"):
                return
            
            # print command or message
            self._log_message(**self.last_string_parsed)
            
            # add the last message to self.last_channel_message,
            self.last_channel_message = self.last_string_parsed["message"]
                
        # run plugin if message was a command
        elif self.last_string_type == "user_command":

            if self.last_string_parsed["command"] in self.commands:
                self._run_plugin(**self.last_string_parsed)
            else:
                # remap command to message and log because command was not valid
                target = self.last_string_parsed["channel"]
                sender = self.last_string_parsed["sender"]
                message = self.last_string_parsed["command"] + \
                    " " + " ".join(self.last_string_parsed["arguments"])
                message = message.rstrip()
                self._log_message(target, sender, message)
    
    def _run_plugin(self, command, sender, arguments, channel):
            
        logging.info('>> {0} issued command "{1} {2}" from {3}'.format(
            sender, command, " ".join(arguments), channel))
            
        plugin = self.commands[command]
        if plugin.needs_admin and sender not in config.admins:
            sorry_string = 'sorry, you need to be an admin to use the "{0}" plugin'
            self.protocol.privmsg(sender, sorry_string.format(plugin.name))
            return

        evaluated_arguments = self._evaluate_arguments(arguments)
        try:
            command_output = plugin.command_function(
                evaluated_arguments, sender, channel)
        except Exception as exc:
            self.say("error: {0}".format(str(exc).lower()))
            logging.exception(exc)
            return
            
        command_output_type = type(command_output).__name__
        if command_output_type == "str":
            self.say(command_output)
            
        elif command_output_type in ("generator", "list"):
            for element in command_output:
                self.say(element)
                
        else:
            self.error('plugin "{0}" returns an unknown object type "{1}"'.format(
                plugin.name, command_output_type))
        
    def _join_channels(self):

        for channel in self.channels:
            if not channel.startswith("#"):
                continue
            self.protocol.join(channel)
            logging.info('joined channel "{0}"'.format(channel))
                    
    def _evaluate_arguments(self, arguments):
        """
        evaluate a list of command arguments for a command
        eg. "the current time is .time" becomes
            "the current time is [current time]"
        """

        arguments_to_return = []

        for argument in arguments:
            if argument not in self.variables:
                arguments_to_return += [argument]
            else:
                variable = argument
                plugin = self.variables[variable]
                variable_value = plugin.variable_function()
                arguments_to_return += [variable_value]

        return arguments_to_return

    def _get_help(self, command):
    
        command_for_help = "." + command
        for c_or_v, list in self.help.items():
            for help_string in list:
                if command_for_help in help_string:
                    self.say("help for {0} {1}:".format(
                        c_or_v, command_for_help))
                    self.say(help_string)
                    return
                    
        self.say('error: could not find help for "{0}"'.format(
            command_for_help))
            
    def _log_message(self, target, sender, message):
        logging.info("[{target}] <{sender}> {message}".format(
            **vars()))

    def load_help(self):
    
        help_file_name = "help.txt"
        
        current_folder = os.path.dirname(__file__)
        provisional_path = os.path.join(current_folder, os.pardir)
        parent_folder = os.path.abspath(provisional_path)
        help_file = os.path.join(parent_folder, "files", help_file_name)
        
        self.help = {}

        with open(help_file) as file:
            for line in file:
                line = line.rstrip()
                if line.startswith("#"):
                    c_or_v = line.strip("#")
                    continue
                if c_or_v not in self.help:
                    self.help[c_or_v] = list = []
                list.append(line)
                
        logging.info('loaded help from file "{0}"'.format(help_file_name))

    def load_plugins(self):
        """
        load all plugins in the "plugins" directory and add
        the command and variable functions in them to self.commands
        and self.variables
        """
    
        current_folder = os.path.dirname(__file__)
        provisional_path = os.path.join(current_folder, os.pardir)
        parent_folder = os.path.abspath(provisional_path)
        plugin_folder = os.path.join(parent_folder, "plugins")

        for file in os.listdir(plugin_folder):

            if file.startswith("_"):
                continue
            elif not file.endswith(".py"):
                continue

            plugin_path = os.path.join(plugin_folder, file)
            plugin_file = imp.load_source(file, plugin_path)

            for class_ in plugin_file.classes:
                plugin = class_(self)
                if hasattr(plugin, "variable"):
                    self.variables[plugin.variable] = plugin
                elif hasattr(plugin, "command"):
                    self.commands[plugin.command] = plugin
                logging.info('loaded plugin "{0}" from file "{1}"'.format(
                    plugin.name, file))

    def say(self, message, channel=None):
    
        if not channel:
            channel = self.last_message_parsed["target"]
        
        # send message
        self.protocol.privmsg(channel, message)
        logging.info('<< replied "{0}"'.format(message))
        # update self.last_channel_message
        self.last_channel_message = message

    def run(self):
        """
        main bot run method, loops and parses IRC commands
        """  
        
        # listen
        while True:
            # receive incoming data from server
            try:
                self.raw_string = self.protocol.recv()
            except RuntimeError as exc:
                logging.exception(exc)
                sys.exit(1)
                
            # PRIVMSG, NOTICE, ect.
            irc_string = IRCString(self.raw_string)
            self.last_string_type = irc_string._get_string_type()
            self.last_string_parsed = irc_string._parse_string()
            
            if self.last_string_type == "user_command":                
                self.last_message_parsed = irc_string._parse_string(
                    parse_for="message")
                
            # perform basic actions like pong, ect.
            self._actions()
