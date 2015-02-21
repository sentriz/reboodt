import urllib.parse
import urllib.request
import json

class Plugin():

    def __init__(self, bot):
        self.name = "qr to url"
        self.command = "qr"
        self.bot = bot
        self.needs_admin = False
        
    def _string_to_qr(self, string):            
        # https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Example
        qr_api_url = "https://api.qrserver.com/v1/create-qr-code/?"
        qr_api_args = {
            "size": "150x150",
            "data": string
        }

        return qr_api_url + urllib.parse.urlencode(qr_api_args)
        
    def _shorten_url(self, url):
        post_url = 'https://www.googleapis.com/urlshortener/v1/url'
        postdata = {
            'longUrl': url
        }
        headers = {
            'Content-Type': 'application/json'
        }
        req = urllib.request.Request(
            post_url,
            str(json.dumps(postdata)).encode(),
            headers
        )
        returned = urllib.request.urlopen(req).read()
        return json.loads(returned.decode())['id']
 
    def run(self, info):
        string = " ".join(info["arguments"])
        if not string:
            self.bot.say("please provide valid arguments")
            return
            
        qr_url = self._string_to_qr(string)
        shortened_url = self._shorten_url(qr_url)
        self.bot.say(shortened_url)
        
if __name__ == "__main__":
    print(Plugin.__doc__)
        