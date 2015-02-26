from files.plugins.__init__ import BasePlugin

class Reload(BasePlugin):
    """
    reboodt plugin for reloading all modules in the
    plugin directory
    usage: .reload
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".reload"
        self.needs_admin = True
 
    def command_function(self, arguments, sender, channel):  
        self.bot.load_plugins()
        return "plugins reloaded"
        
classes = (Reload,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)