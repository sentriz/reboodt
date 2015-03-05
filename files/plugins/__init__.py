import urllib.request
import json

class BasePlugin:

    def __init__(self, bot):
        self.name = type(self).__name__
        self.bot = bot
        self.needs_admin = False
        
    def _shorten_url(self, url):
        post_url = 'https://www.googleapis.com/urlshortener/v1/url'
        post_data = {
            'longUrl': url
        }
        headers = {
            'Content-Type': 'application/json'
        }
        
        json_post_data = json.dumps(post_data)
        encoded_post_data = str(json_post_data).encode()
        req = urllib.request.Request(
            post_url,
            encoded_post_data,
            headers
        )
        
        opened_url = urllib.request.urlopen(req)
        opened_url_data = opened_url.read()
        decoded_data = opened_url_data.decode()
        json_data = json.loads(decoded_data)
        url = json_data["id"]
        
        return url
        
class BaseVariable:

    def __init__(self, bot):
        self.name = type(self).__name__
        self.bot = bot
