# Bot() based on Alec Hussey's PyBotlib
# last_channel_message

from lib.irc import Protocol
from lib.parsing import IRCString
from lib.parsing import PluginManager

import logging
import sys


class Bot():

    def __init__(self, server, port, channels,
                 nick, network_name, password, admins):

        logging.info('initialising "{0}" bot'.format(network_name))

        # initialise IRC protocol
        self.protocol = Protocol(server, port)
        self.protocol.identify(nick)

        # initialise plugins
        self.plugins = PluginManager(bot=self)
        self.plugins.load()
        self.plugins.load_help()

        # initialise class variables
        self.server = server
        self.port = port
        self.channels = channels
        self.nick = nick
        self.network_name = network_name
        self.password = password
        self.admins = admins

        # misc
        self.in_channels = False
        self.last_message = ""

    def _actions(self):
        """
        loop that listens and performs defined commands
        """

        # check for and respond to PING requests
        if self.string.type == "ping":
            pong = self.string.parsed["pong"]
            self.protocol.send("PONG :" + pong)
            if not self.in_channels:
                for channel in self.channels:
                    if not channel.startswith("#"):
                        continue
                    logging.info('joining channel "{0}"'.format(channel))
                    self.protocol.join(channel)
                self.in_channels = True

        elif self.string.type == "notice":
            if not self.password:
                return
            # hook NickServ asking for authentication
            # "this nickname is registered".. "please choose"..
            if "choose a different" in self.raw_string:
                self.protocol.privmsg("NickServ", "identify " + self.password)
                hidden_password = "*" * len(self.password)
                logging.info(
                    "identifed with NickServ with pass " + hidden_password)

        elif self.string.type == "message":
            # ignore junky startup messages by ensuring
            # channel starts with "#"
            channel = self.string.parsed["target"]
            if not channel.startswith("#"):
                return
            # print command or message
            self._log_message(**self.string.parsed)
            # add the last channel message to self.last_message
            # this is used by the .last variable
            self.last_message = self.string.parsed["message"]

        # run plugin if message was a command
        elif self.string.type == "user_command":
            logging.info('>> {0} issued command "{1}" from {2}'.format(
                self.string.command_as_message["sender"],
                self.string.command_as_message["message"],
                self.string.command_as_message["target"]))
            if self.string.parsed["command"] in self.plugins.commands:
                output = self.plugins.run(**self.string.parsed)
                if not output:
                    return
                output_type = type(output).__name__
                if output_type == "str":
                    self.say(output)
                else:
                    for line in output:
                        self.say(line)
            else:
                logging.info('<< "{0}" is not a plugin command'.format(
                    self.string.parsed["command"]))

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
            **locals()))

    def say(self, message, channel=None):
        if not channel:
            channel = self.string.command_as_message["target"]
        # send message
        self.protocol.privmsg(channel, message)
        logging.info('<< replied "{0}"'.format(message))
        # update self.last_channel_message
        self.last_message = message

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
            # perform basic actions like pong, ect.
            self._actions()
