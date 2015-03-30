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


class UserInfo(BaseCommand):

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
            user=urllib.parse.quote(user)
        )

        if not "user" in user_data:
            return '"{0}" is not a last.fm user'.format(user)
        else:
            user_info = user_data["user"]
            info_strings = self._generate_info(user_info)
            return info_strings


class UserNP(BaseCommand):

    """
    reboodt plugin that tries to find now playing info on a given user
    usage: .fmnp user
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = ".fmnp"

    def _generate_info(self, tracks_data):
        recent_tracks = tracks_data["recenttracks"]
        last_track = recent_tracks["track"][0]
        formatted_user = recent_tracks["@attr"]["user"]
        now_playing = False

        if "@attr" in last_track:
            if "nowplaying" in last_track["@attr"]:
                if last_track["@attr"]["nowplaying"]:
                    now_playing = True

        if now_playing:
            yield 'user "{0}" is now playing:'.format(
                formatted_user)
        else:
            yield 'user "{0}" is not playing anything right now.'.format(
                formatted_user) + " last track was:"

        main_line = '"' + last_track["name"] + '"'
        if "artist" in last_track:
            main_line += " by " + last_track["artist"]["#text"]

        yield main_line

        if "album" in last_track:
            yield 'from the album "{0}"'.format(last_track["album"]["#text"])

        if "url" in last_track:
            url = last_track["url"]
            yield "track page: " + self._shorten_url(url)

    def command_function(self, arguments, sender, channel):
        user = arguments[0] if arguments else None
        if not user:
            return "please provide a user"

        tracks_data = get_lastfm_data(
            self.api_keys["lastfm"],
            "user.getrecenttracks",
            user=urllib.parse.quote(user)
        )

        if "recenttracks" not in tracks_data:
            return '"{0}" is not a last.fm user'.format(user)
        else:
            info_strings = self._generate_info(tracks_data)
            return info_strings

classes = (UserInfo, UserNP)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
