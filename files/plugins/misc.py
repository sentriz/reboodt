from files.plugins.__init__ import BaseCommand

class Say(BaseCommand):
    """
    reboodt plugin, say a string given
    usage: .say this is a string
    result: this is a string
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".say"
 
    def command_function(self, arguments, sender, channel):
        string = " ".join(arguments)
        return string
        
classes = (Say,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)