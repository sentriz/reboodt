import botlib
import config

class UserBot(botlib.Bot):

    def _actions(self):
        super()._actions()

        if self.get_string_type() == "command":
            full_command = self.parse_string()
            command = full_command["command"]
            args = full_command["arguments"]

            if command == "!hello":
                if args:
                    self.greet(args[0])
                else:
                    nick = self.parse_string("PRIVMSG")["sender"]
                    self.greet(nick)
            elif command == "!quit":
                if args:
                    self.protocol.disconnect(message=" ".join(args))
                else:
                    self.protocol.disconnect(message="bye")

    def greet(self, username):
        self.say("Hello, {}!".format(username))

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
            reboodt.run()