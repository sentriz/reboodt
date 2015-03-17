from lib.bot import Bot
from lib.utilities import load_yaml
import logging
import os
import sys
import threading
import time

class UserBot(Bot):

    def _actions(self):
        """
        loop that listens and performs user defined commands
        """

        super()._actions()

        if not self.string.type == "user_command":
            return

        command = self.string.parsed["command"]
        sender = self.string.parsed["sender"]
        arguments = self.string.parsed["arguments"]
        channel = self.string.parsed["channel"]

        if command == ".join" and sender in admins:
            channels = arguments
            if not channels:
                self.say("please provide at least one channel")
                return
            for channel_ in channels:
                if not channel_.startswith("#"):
                    self.say('"{0}" is not a #channel'.format(
                        channel_))
                    continue
                self.protocol.join(channel_)
                self.say("in channel " + channel_)

        elif command == ".quit" and sender in admins:
            reason = " ".join(arguments) or "disconnect"
            self.protocol.disconnect(reason)

        elif command == ".reload" and sender in admins:
            self.plugins.load()
            self.plugins.load_help()
            self.say("plugins/help file reloaded")

        elif command == ".ping":
            self.say("pong!")

        elif command == ".help":
            if not arguments:
                self.say("commands: " + ", ".join(self.commands))
                self.say("variables: " + ", ".join(self.variables))
                self.say('use ".help [command/variable name]" to read more')
            else:
                command_for_help = arguments[0]
                self._get_help(command_for_help)

if __name__ == "__main__":

    logging.basicConfig(
        format="[%(asctime)s] %(threadName)s: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO
    )

    try:
        config = load_yaml("config.yml")
    except FileNotFoundError:
        logging.critical("could not find config.yml")
        sys.exit(1)

    servers = config["servers"]
    admins = config["admins"]

    enabled_servers = [server["connect"] for _, server in servers.items()]
    if not any(enabled_servers):
        logging.critical("no servers enabled to connect to in config.yml")
        sys.exit(1)

    for name, server in servers.items():

        if not server["connect"]:
            continue

        reboodt = UserBot(
            server = server["host"],
            port = server["port"],
            channels = server["channels"],
            nick = server["nick"],
            network_name = name,
            password = server["password"]
        )

        server_thread = threading.Thread(
            None, target=reboodt.run, name=name)
        server_thread.start()

    try:
        while True:
            time.sleep(5)

    except (SystemExit, KeyboardInterrupt):
        logging.warning("program was closed")
        sys.exit()
