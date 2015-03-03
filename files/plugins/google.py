from files.plugins.__init__ import BasePlugin
import urllib.request
import urllib.parse
import json


class Google(BasePlugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".google"
        
    def _google_search(self, query):
        base_url = 'http://ajax.googleapis.com/ajax/services/search/web?'
        quoted_query = urllib.parse.quote(query)
        url_encoding = {
            "q": quoted_query,
            "v": "1.0"
        } 
        url = base_url + urllib.parse.urlencode(url_encoding)
                
        response = urllib.request.urlopen(url).read()
        response_json = json.loads(response.decode())
        response_data = response_json["responseData"]
        
        return response_data
        
 
    def command_function(self, arguments, sender, channel):
        if not arguments:
            return "please provide a search query"
            
        query = " ".join(arguments)
        response_data = self._google_search(query)
        
        results = response_data["results"]
        result_count = response_data["cursor"]["resultCount"]
        time = response_data["cursor"]["searchResultTime"]

        yield '{0} results for "{1}" in {2}s'.format(
            result_count, query, time)
        for result in results:
            yield "{1} ({0})".format(
                result["visibleUrl"], result["titleNoFormatting"]
            )
        
classes = (Google,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
        