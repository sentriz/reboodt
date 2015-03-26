from plugins.__init__ import BaseCommand
import urllib.parse
import html

class WolframAlpha(BaseCommand):
    """
    reboodt plugin using the Wolfram|Alpha calculator
    usage: .c 5 + 2
    result: 7
    """
    
    command = ".calc"
        
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
        if not arguments:
            return "please provide a query to calculate"
        string = " ".join(arguments)
        string = string.replace("+", "plus")
        results = self._calculate(string).split(";")
        
        if len(results) >= 2:
            left = results[0]
            right = results[1]
            return "{0} = {1}".format(left, right)
        else:
            return "no results found"
        
classes = (WolframAlpha,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)