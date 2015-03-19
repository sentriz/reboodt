from plugins.__init__ import BaseCommand
import json
import urllib.parse

def get_lastfm_data(api_key, api_method, **kwargs):

    base_url = "http://ws.audioscrobbler.com/2.0/?"
    lastfm_api_args = {
        "api_key": api_key,
        "format": "json",
        "method": api_method
    }
    
    all_api_args = dict(lastfm_api_args.items() | kwargs.items())
    url = base_url + urllib.parse.urlencode(all_api_args)

    response = urllib.request.urlopen(url).read()
    response_json = json.loads(response.decode())
    
    return response_json


class User(BaseCommand):
    """
    reboodt plugin that displays information about a lastfm user
    usage: .fmu user
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = ".fmu"
       
    def _generate_info(self, user_info):
        info_list, image_url = [], ""

        yield 'info for last.fm user "{0}":'.format(user_info["name"])
        
        if "realname" in user_info and user_info["realname"]:
            yield "real name: " + user_info["realname"]
        
        for key in ("age", "gender", "country", "playcount"):
            if key in user_info and user_info[key]:
                info_list.append("{0}: {1}".format(key, user_info[key]))
        yield " | ".join(info_list)
        
        for image_dict in user_info["image"]:
            if image_dict["size"] == "large":
                image_url = image_dict["#text"]
                break
        if image_url:
            yield "image: " + self._shorten_url(image_url)
            
        yield "url: " + user_info["url"]

    def command_function(self, arguments, sender, channel):
        user = arguments[0] if arguments else None
        if not user:
            return "please provide a user"

        user_data = get_lastfm_data(
            self.api_keys["lastfm"],
            "user.getinfo",
            user = urllib.parse.quote(user)
        )
        
        if not "user" in user_data:
            return '"{0}" is not a last.fm user'.format(user)
        else:
            user_info = user_data["user"]
            info_strings = self._generate_info(user_info)
            return info_strings

classes = (User,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
