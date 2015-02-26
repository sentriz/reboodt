from files.plugins.__init__ import BasePlugin
from datetime import datetime

class Calc(BasePlugin):
    """
    reboodt plugin using the frink calculator
    usage: .c 5 + 2
    result: 7
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".calc"
        
    def _calculate(self, string):
        return "21"
        
    def command_function(self, arguments, sender, channel):
        string = arguments
        return self._calculate(string)
        
classes = (Calc,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)