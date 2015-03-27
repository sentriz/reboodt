from plugins.__init__ import BaseCommand
from lib.merriam_webster_api import CollegiateDictionary, WordNotFoundException

class MerriamWebster(BaseCommand):
    """
    reboodt plugin that defines a given word
    usage: .define word
    """

    command = ".define"

    def _lookup(self, query):
        api_key = self.api_keys["merriam_webster_collegiate"]
        dictionary = CollegiateDictionary(api_key)
        definitions = []
        try:
            for entry in dictionary.lookup(query):
                for definition, examples in entry.senses:
                    if len(definitions) > 4:
                        break
                    to_append = (entry.word, entry.function, definition)
                    definitions.append(to_append)
        except WordNotFoundException as exc:
            return_string = 'no definitions found for "{0}". '.format(query)
            if exc.suggestions:
                short_suggestions = exc.suggestions[:5]
                return_string += "did you mean "
                if len(short_suggestions) == 1:
                    return_string += '"' + short_suggestions[0] + '"'
                else:
                    return_string += '"' + '", "'.join(short_suggestions[:-1]) 
                    return_string += '"' + ' or "' + short_suggestions[-1] + '"'
                return_string += "?"
            yield return_string
            return
        for word, function, definition in definitions:
            yield "[{0}|{1}] {2}".format(word, function, definition)

    def command_function(self, arguments, sender, channel):
        query = " ".join(arguments)
        if not query:
            return "please provide a word to define"
        if not "merriam_webster_collegiate" in self.api_keys:
            api_register_url = "http://www.dictionaryapi.com/register/index.htm"
            string = "please get a Merriam Webster Collegiate API key"
            string += " " + self._shorten_url(api_register_url)
            return string
        definitions = self._lookup(query)
        return definitions

classes = (MerriamWebster,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
