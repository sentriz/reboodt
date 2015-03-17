from plugins.__init__ import BaseCommand
import urllib.request
import urllib.parse
import json


class Google(BaseCommand):
    """
    reboodt plugin that googles a search query
    usage: .google query
    """


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
        
    def _make_results_generator(self, response_data, user_query):       
        results = response_data["results"]
        if not "resultCount" in response_data["cursor"]:
            yield 'no results found for "{0}"'.format(user_query)
            return
        result_count = response_data["cursor"]["resultCount"]
        time = response_data["cursor"]["searchResultTime"]

        yield '{0} results for "{1}" in {2}s:'.format(
            result_count, user_query, time)
        for result in results:
            yield "{1} ({0})".format(
                result["url"], result["titleNoFormatting"]
            )    
 
    def command_function(self, arguments, sender, channel): 
        if not arguments:
            return "please provide a search query"
            
        query = " ".join(arguments)
        response_data = self._google_search(query)
        results_generator = self._make_results_generator(
            response_data, query)
        
        return results_generator
        

        
classes = (Google,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
        