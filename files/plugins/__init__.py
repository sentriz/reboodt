import urllib.request
import json

class BasePlugin:

    def __init__(self, bot):
        self.name = type(self).__name__
        self.bot = bot
        self.needs_admin = False
        
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
        
class BaseVariable:

    def __init__(self, bot):
        self.name = type(self).__name__
        self.bot = bot
