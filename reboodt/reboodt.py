from lib.bot import Bot
import config
import imp
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
        
        if not self.last_string_type == "user_command":
            return

        command = self.last_string_parsed["command"]
        sender = self.last_string_parsed["sender"]
        arguments = self.last_string_parsed["arguments"]
        channel = self.last_string_parsed["channel"]

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
