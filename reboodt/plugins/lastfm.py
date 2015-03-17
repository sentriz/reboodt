from plugins.__init__ import BaseCommand
import json
import urllib.parse

class User(BaseCommand):
    """
    reboodt plugin that displays information about a lastfm user
    usage: .fmu user
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = ".fmu"

    def _get_data(self, user):
        quoted_user = urllib.parse.quote(user)

        base_url = "http://ws.audioscrobbler.com/2.0/?"
        lastfm_api_args = {
            "api_key": self.api_keys["lastfm"],
            "format": "json",
            "method": "user.getinfo",
            "user": quoted_user
        }

        url = base_url + urllib.parse.urlencode(lastfm_api_args)

        response = urllib.request.urlopen(url).read()
        response_json = json.loads(response.decode())
        return response_json

    def command_function(self, arguments, sender, channel):
        user = arguments[0] if arguments else None
        if not user:
            yield "please provide a user"
            return
        
        user_data = self._get_data(user)
        if not "user" in user_data:
            yield '"{0}" is not a last.fm user'.format(user)
            return
        else:
            user_info = user_data["user"]
            
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

classes = (User,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
