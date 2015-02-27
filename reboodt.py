from files.botlib import Bot
import files.config as config

import imp
import os

class UserBot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.commands = {}
        self.variables = {}
        self.help = {}

    def _actions(self):
        """
        loop that listens and performs user defined actions
        """

        super()._actions()

        if not self.get_string_type() == "command":
            return

        parsed_string = self.parse_string()
        command = parsed_string["command"]
        sender = parsed_string["sender"]
        arguments = parsed_string["arguments"]
        channel = parsed_string["channel"]

        if command == ".join" and sender in config.admins:
            if not arguments:
                self.say("please provide at least one channel")
                return
            channels = arguments
            for channel_ in channels:
                self.protocol.join(channel_)

        elif command == ".quit" and sender in config.admins:
            reason = " ".join(arguments)
            reason = reason or "disconnect"
            self.protocol.disconnect(reason)

        elif command == ".help":
            if not arguments:
                self.say("commands: " + ", ".join(self.commands))
                self.say("variables: " + ", ".join(self.variables))
            else:
                command_for_help = arguments[0]
                self._get_help(command_for_help)

        if not command in self.commands:
            return

        plugin = self.commands[command]

        if plugin.needs_admin and sender not in config.admins:
            sorry_string = "sorry, you need to be an admin to use the {0} plugin"
            self.protocol.privmsg(sender, sorry_string.format(plugin.name))
            return

        try:
            evaluated_arguments = self._evaluate_arguments(arguments)
            command_output = plugin.command_function(
                evaluated_arguments, sender, channel)
            self.say(command_output)

        except Exception as e:
            self.say("error: {0}".format(str(e).lower()))
            self.say("     - {0}".format(str(e.__doc__).lower()))
            #raise


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
                    self.say("help for {0} {1}:".format(c_or_v, command_for_help))
                    self.say(help_string)
                    return
        self.say('could not find help for "{0}"'.format(
            command_for_help))

    def load_help(self):
        current_folder = os.path.dirname(__file__)
        help_file = os.path.join(current_folder, "files", "help.txt")

        with open(help_file) as file:
            for line in file:
                line = line.rstrip()
                if line.startswith("#"):
                    c_or_v = line.strip("#")
                    continue
                if c_or_v not in self.help:
                    self.help[c_or_v] = list = []
                list.append(line)

    def load_plugins(self):
        """
        load all plugins in the "plugins" directory and add
        the command and variable functions in them to self.commands
        and self.variables
        """

        current_folder = os.path.dirname(__file__)
        plugin_folder = os.path.join(current_folder, "files", "plugins")

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
                print('plugin "{0}" from file "{1}" loaded'.format(
                    plugin.name, file))

if __name__ == "__main__":

    for server in config.servers:
        if server["connect"]:
            reboodt = UserBot(
                server["host"],
                server["port"],
                server["chans"],
                server["nick"],
                server["name"],
                server["auth"]
            )
            reboodt.load_plugins()
            reboodt.load_help()
            reboodt.run()
