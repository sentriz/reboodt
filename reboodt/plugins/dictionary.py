from plugins.__init__ import BaseCommand
import urllib.parse
import urllib.request
import xmltodict
import collections

class MerriamWebster(BaseCommand):
    """
    reboodt plugin that defines a given word
    usage: .define word
    """

    command = ".define"
    
    def _get_definitions(self, word):
        base_url = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{word}?"
        quoted_word = urllib.parse.quote(word)
        base_url = base_url.format(word=word)
        url_encoding = {
            "key": self.api_keys["merriam_webster"]
        }
        url = base_url + urllib.parse.urlencode(url_encoding)
        response = urllib.request.urlopen(url).read()
        xml = xmltodict.parse(response)
        
        word = xml["entry_list"]["entry"]["ew"]
        pronunciation = xml["entry_list"]["entry"]["hw"]
        definitions = xml["entry_list"]["entry"]["def"]["dt"]
        definition_list = []
        
        for definition in definitions:
            if isinstance(definition, collections.OrderedDict):
                def_word_list = definition["#text"].split(" ")
                removals_list = []
                for key, value in definition.items():
                    if key != "#text":
                        removals_list.append(value)
                for n, word in enumerate(def_word_list):
                    if not word:
                        del def_word_list[n]
                        def_word_list.insert(n, removals_list.pop())
                definition_list.append(" ".join(def_word_list))
            else:
                definition_list.append(definition)
        for definition in definition_list:
            type = definition[1]
            definition = " ".join(definition.split()[1:])
            yield "[{0}] {1}".format(type, definition)

    def command_function(self, arguments, sender, channel):
        word = arguments[0] if arguments else None
        if not word:
            return "please provide a word"
        if not "merriam_webster" in self.api_keys:
            return "please get a Merriam Webster API key"
        return self._get_definitions(word)

classes = (MerriamWebster,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
