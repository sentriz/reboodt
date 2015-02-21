from datetime import datetime

class Plugin():
    """
    reboodt plugin for saying the current time
    """

    def __init__(self, bot):
        self.name = "time"
        self.command = "time"
        self.bot = bot
        self.needs_admin = False
 
    def run(self, info):
        time_format = "%Y/%m/%d %H:%M:%S"
        time_string = datetime.now().strftime(time_format)
        self.bot.say(time_string)
        
if __name__ == "__main__":
    print(Plugin.__doc__)