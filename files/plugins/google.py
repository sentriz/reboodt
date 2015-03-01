from files.plugins.__init__ import BasePlugin
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

class Google(BasePlugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".google"
        
    def _google_search(self, query):
        # Create opener with Google-friendly user agent
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        # Open page & generate soup
        base_url = "http://www.google.com/search?"
        quoted_query = urllib.parse.quote(query)
        url_encoding = {
            "q": quoted_query
        } 
        url = base_url + urllib.parse.urlencode(url_encoding)
        page = opener.open(url)
        soup = BeautifulSoup(page)

        # Parse and find
        # Looks like google contains URLs in <cite> tags.
        # So for each cite tag on each page (10), print its contents (url)
        search_div = soup.find(id='search')
        anchors = search_div.findAll('a')
        
        for anchor in anchors:
            try:
                link = anchor["href"]
            except KeyError:
                continue
                
            # skip non-absolute URLs
            parsed_link = urllib.parse.urlparse(link, 'http')
            if parsed_link.netloc and 'google' in parsed_link.netloc:
                continue
                    
            # Decode hidden URLs
            if link.startswith('/url?'):
                parsed_query = urllib.parse.parse_qs(parsed_link.query)
                link_list = parsed_query['q']
                link = link_list[0]
                yield link
 
    def command_function(self, arguments, sender, channel):
        if not arguments:
            return "please provide a search query"
            
        query = " ".join(arguments)
        links = self._google_search(query)
        
        for link in links:
            yield link
        
classes = (Google,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)