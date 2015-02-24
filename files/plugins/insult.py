from files.plugins.__init__ import BasePlugin
import random
import os

class Insult(BasePlugin):
    """
    reboodt plugin, a shakespearean insult generator
    (insults from github/0x27/hexchat-shakespeare-insult)
    usage: .insult [user]
    result: user, thou x y z!
    or.. if no user is supplied..
    result: thou x y z!
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = ".insult"
        self.insults = [[], [], []]
        
        self._load_insults()
        
    def _load_insults(self):
        current_folder = os.path.dirname(__file__)
        provisional_path = os.path.join(current_folder, os.pardir)
        parent_folder = os.path.abspath(provisional_path)
        insults_file = os.path.join(parent_folder, "insults.txt")
        
        with open(insults_file) as file:
            for line in file:
                line = line.rstrip()
                if line == "#first":
                    append_to = self.insults[0]
                    continue
                elif line == "#second":
                    append_to = self.insults[1]
                    continue
                elif line == "#third":
                    append_to = self.insults[2]
                    continue
                append_to.append(line)
                
    def command_function(self, info):
        arguments = info["arguments"]
        user = arguments[0] if arguments else None
        
        first_word = random.choice(self.insults[0])
        second_word = random.choice(self.insults[1])
        third_word = random.choice(self.insults[2])
        
        insult = "{0} {1} {2}".format(
            first_word, second_word, third_word)
            
        print(self.insults)
            
        if user:
            return user + ", thou " + insult + "!"
        else:
            return "thou " + insult + "!"
        
classes = (Insult,)
        
if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)