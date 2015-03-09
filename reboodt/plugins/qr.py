from plugins.__init__ import BaseCommand
import urllib.parse

class QR(BaseCommand):
    """
    reboodt plugin for creating a qr code from a string
    usage: .qr [string for qr code]
    result: http://goo.gl/xxxxxx
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".qr"
        
    def _string_to_qr(self, string):            
        # https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Example
        qr_api_url = "https://api.qrserver.com/v1/create-qr-code/?"
        qr_api_args = {
            "size": "150x150",
            "data": string
        }

        return qr_api_url + urllib.parse.urlencode(qr_api_args)
 
    def command_function(self, arguments, sender, channel):
        string = " ".join(arguments)
        if not string:
            self.bot.say("please provide valid arguments")
            return
            
        qr_url = self._string_to_qr(string)
        shortened_url = self._shorten_url(qr_url)
        return shortened_url
        
classes = (QR,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
        