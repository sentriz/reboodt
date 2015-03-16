from lib.utilities import load_yaml
import json
import urllib.request

class BaseCommand:

    def __init__(self, bot):
        self.name = type(self).__name__
        self.bot = bot
        self.needs_admin = False
        self.api_keys = load_yaml("api_keys.yml")

    def _shorten_url(self, url):
        post_url = 'https://www.googleapis.com/urlshortener/v1/url?'
        
        api_key = self.api_keys["googl_shortner"]

        if api_key:
            url_encoding = {
                'key': api_key
            } 
            post_url += urllib.parse.urlencode(url_encoding)
        
        post_data = {
            'longUrl': url
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

    def command_function(self, arguments, sender, channel):
        raise NotImplementedError

class BaseVariable:

    def __init__(self, bot):
        self.name = type(self).__name__
        self.bot = bot

    def variable_function(self):
        raise NotImplementedError
