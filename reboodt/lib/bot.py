# Bot() based on Alec Hussey's PyBotlib

import config
from lib.irc import Protocol
from lib.parsing import IRCString
from lib.parsing import PluginManager
import logging
import os
import sys

class Bot():

    def __init__(self, server, port, channels,
            nick, network_name, authentication):

        logging.info('initialising "{0}" bot'.format(network_name))

        # initialise IRC protocol
        self.protocol = Protocol(server, port)
        self.protocol.identify(nick)
        
        # initialise plugins
        self.plugins = PluginManager()
        self.plugins.load()
        self.plugins.load_help()

        # initialise class variables
        self.server = server
        self.port = port
        self.channels = channels
        self.nick = nick
        self.network_name = network_name
        self.authentication = authentication

        # misc booleans
        self.in_channels = False


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

            logging.info('>> {0} issued command "{1}" from {2}'.format(
                self.last_string_parsed["sender"], 
                self.last_message_parsed["message"], 
                self.last_message_parsed["target"]
                )
            )
            if self.last_string_parsed["command"] in self.plugins.commands:
                command_output = self.plugins.run(**self.last_string_parsed)
                command_output_type = type(command_output).__name__
                
                if command_output_type == "str":
                    self.say(command_output)
                elif command_output_type in ("generator", "list"):
                    for line in command_output:
                        self.say(line)
                else:
                    logging.error('plugin "{0}" returns an unknown object type "{1}"'.format(
                        plugin.name, command_output_type))
                
            else:
                logging.info('<< "{0}" is not a plugin command'.format(
                    self.last_string_parsed["command"]
                    )
                )

    def _join_channels(self):

        for channel in self.channels:
            if not channel.startswith("#"):
                continue
            self.protocol.join(channel)
            logging.info('joined channel "{0}"'.format(channel))

    def _get_help(self, command):

        command_for_help = "." + command
        
        for c_or_v, list in self.plugins.help.items():
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
            self.string = IRCString(self.raw_string)
            self.last_string_type = self.string._get_type()
            self.last_string_parsed = self.string._parse()

            if self.last_string_type == "user_command":
                self.last_message_parsed = self.string._parse(
                    parse_for="message")

            # perform basic actions like pong, ect.
            self._actions()
