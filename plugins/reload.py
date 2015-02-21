class Plugin():
    """
    reboodt plugin for reloading all modules in the
    plugin directory
    """

    def __init__(self, bot):
        self.name = "reload"
        self.command = "reload"
        self.bot = bot
        self.needs_admin = True
 
    def run(self, info):      
        self.bot.load_plugins()
        self.bot.say("plugins reloaded")
        
if __name__ == "__main__":
    print(Plugin.__doc__)