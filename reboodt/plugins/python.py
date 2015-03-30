from plugins.__init__ import BaseCommand
import urllib.parse


class Python(BaseCommand):

    """
    reboodt plugin that evaluates a python expression
    usage: .py 1 + 2
    result: 3
    """

    command = ".py"

    def _evaluate(self, string):
        base_url = "http://tumbolia.appspot.com/py/"
        url = base_url + urllib.parse.quote(string)
        response_data = urllib.request.urlopen(url)
        encoded_response = response_data.read()
        response = encoded_response.decode()
        response = response.rstrip()
        return response

    def command_function(self, arguments, sender, channel):
        string = " ".join(arguments)
        if not string:
            return "please provide a valid python expression"
        result = self._evaluate(string)
        return result

classes = (Python,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
