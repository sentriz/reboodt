from lib.bot import Bot
import config
import imp
import logging
import os
import sys
import threading
import time

class UserBot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        logging.info('initialising "{0}" bot'.format(
            self.network_name))

        self.commands = {}
        self.variables = {}
        self.help = {}
        
        self.load_plugins()
        self.load_help()
        
    def _actions(self):
        """
        loop that listens and performs user defined commands
        """

        super()._actions()

        if not self.last_command_type == "user_command":
            return
        print("here")

        command = self.last_command_parsed["command"]
        sender = self.last_command_parsed["sender"]
        arguments = self.last_command_parsed["arguments"]
        channel = self.last_command_parsed["channel"]

        if command == ".join" and sender in config.admins:
            channels = arguments
            if not arguments:
                self.say("please provide at least one channel")
                return
            for channel_ in channels:
                self.protocol.join(channel_)

        elif command == ".quit" and sender in config.admins:
            reason = " ".join(arguments)
            reason = reason or "disconnect"
            self.protocol.disconnect(reason)
            
        elif command == ".reload" and sender in config.admins:
            self.load_plugins()
            self.load_help()
            self.say("plugins/help file reloaded")

        elif command == ".help":
            if not arguments:
                self.say("commands: " + ", ".join(self.commands))
                self.say("variables: " + ", ".join(self.variables))
                self.say('use ".help [command/variable name]" to read more')
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

        evaluated_arguments = self._evaluate_arguments(arguments)
        try:
            command_output = plugin.command_function(
                evaluated_arguments, sender, channel)
        except Exception as exc:
            self.say("error: {0}".format(str(exc).lower()))
            self.say("     - {0}".format(str(exc.__doc__).lower()))
            logger.exception(exc)
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
                    
        self.say('error: could not find help for "{0}"'.format(
            command_for_help))

    def load_help(self):
        current_folder = os.path.dirname(__file__)
        help_file_name = "help.txt"
        help_file = os.path.join(current_folder, "files", help_file_name)
        
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
        plugin_folder = os.path.join(current_folder, "plugins")

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

if __name__ == "__main__":

    logging.basicConfig(
        format="[%(asctime)s] %(threadName)s: %(message)s", 
        datefmt="%H:%M:%S", 
        level=logging.INFO
    )
    
    enabled_servers = [server["connect"] for server in config.servers]
    if not any(enabled_servers):
        logging.critical("no servers enabled to connect to in config.py")
        sys.exit(1)

    for server in config.servers:

        if not server["connect"]:
            continue

        reboodt = UserBot(
            server = server["host"],
            port = server["port"],
            channels = server["chans"],
            nick = server["nick"],
            network_name = server["name"],
            authentication = server["auth"]
        )

        server_thread = threading.Thread(
            None, target=reboodt.run, name=server["name"])
        server_thread.start()
    
    try:
        while True:
            time.sleep(5)
    except (SystemExit, KeyboardInterrupt):
        logging.warning("program was closed")
        sys.exit()
