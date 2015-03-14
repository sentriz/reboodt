import logging
import os
import imp
import config

class IRCString:

    def __init__(self, raw_string):

        self.raw_string = raw_string

    def _parse(self, parse_for=None):

        parse_for = parse_for or self._get_type()

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

    def _get_type(self):

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

class PluginManager:

    def __init__(self):
        self.commands = {}
        self.variables = {}
        self.help = {}

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

    def load(self):
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

    def run(self, command, sender, arguments, channel):

        plugin = self.commands[command]
        if plugin.needs_admin and sender not in config.admins:
            sorry_string = '{0}: you need to be an admin to use the "{0}" plugin'
            return sorry_string.format(sender, plugin.name)

        evaluated_arguments = self._evaluate_arguments(arguments)
        try:
            command_output = plugin.command_function(
                evaluated_arguments, sender, channel)
        except Exception as exc:
            logging.exception(exc)
            return "error: {0}".format(str(exc).lower())
            
        return command_output
