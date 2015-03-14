from plugins.__init__ import BaseCommand
import urllib.parse
import html

class Calc(BaseCommand):
    """
    reboodt plugin using the wolfram alpha calculator
    usage: .c 5 + 2
    result: 7
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".calc"
        
    def _calculate(self, string):
        base_url = "http://tumbolia.appspot.com/wa/"
        
        url = base_url + urllib.parse.quote(string)
        response_data = urllib.request.urlopen(url)
        encoded_response = response_data.read()
        response = encoded_response.decode()
        response = response.rstrip()
        unescaped_response = html.unescape(response)
        
        return unescaped_response
        
    def command_function(self, arguments, sender, channel):
        string = " ".join(arguments)
        string = string.replace("+", "plus")
        results = self._calculate(string).split(";")
        
        left = results[0]
        right = results[1]
        
        yield "{0} = {1}".format(left, right)
        
classes = (Calc,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)