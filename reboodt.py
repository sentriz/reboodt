import botlib
import config
import imp
import os

class UserBot(botlib.Bot):

    def __init__(self, *args, **kwargs):
        botlib.Bot.__init__(self, *args, **kwargs)
        
        self.commands = {}

    def _actions(self):
        botlib.Bot._actions(self)

        if self.get_string_type() == "command":
            parsed_string = self.parse_string()
            command = parsed_string["command"]
            sender = parsed_string["sender"]
            arguments = parsed_string["arguments"]
            
            if command == "join" and sender in config.admins:
                if not arguments:
                    return
                self.protocol.join(arguments[0])
                
            elif command == "quit" and sender in config.admins:
                self.protocol.disconnect()
                
        else:
            return
            
        if command in self.commands:
            plugin = self.commands[command]
            if plugin.needs_admin and sender not in config.admins:
                sorry_string = "sorry, you need to be an admin to perform that command"
                self.protocol.privmsg(sender, sorry_string)
                return
            try:
                plugin.run(parsed_string)
            except Exception as e:
                self.say("error: {0}\n{1}".format(e, e.__doc__))
                #raise
                
    def load_plugins(self):
        current_folder = os.path.dirname(__file__)
        plugin_folder = os.path.join(current_folder, "plugins")

        for file in os.listdir(plugin_folder):

            if file.startswith("_"):    
                continue
            elif not file.endswith(".py"):    
                continue
                
            plugin_path = os.path.join(plugin_folder, file)
            plugin = imp.load_source(file, plugin_path).Plugin(self)
            self.commands[plugin.command] = plugin
            print("* plugin \"{}\" loaded".format(plugin.name))

if __name__ == "__main__":

    for server in config.servers:
        if server["connect"]:
            reboodt = UserBot(
                server["host"],
                server["port"],
                server["chans"],
                server["nick"],
                server["name"]
            )
            reboodt.load_plugins()
            reboodt.run()
            