from plugins.__init__ import BaseCommand
import random
import os


class Insult(BaseCommand):

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
        self.insults = {}

        self._load_insults()

    def _load_insults(self):
        current_folder = os.path.dirname(__file__)
        provisional_path = os.path.join(current_folder, os.pardir)
        parent_folder = os.path.abspath(provisional_path)
        insults_file = os.path.join(parent_folder, "files", "insults.txt")

        with open(insults_file) as file:
            for line in file:
                line = line.rstrip()
                if line.startswith("#"):
                    word_pos = line.strip("#")
                    continue
                if word_pos not in self.insults:
                    self.insults[word_pos] = list = []
                list.append(line)

    def command_function(self, arguments, sender, channel):
        user = arguments[0] if arguments else None

        first_word = random.choice(self.insults["first"])
        second_word = random.choice(self.insults["second"])
        third_word = random.choice(self.insults["third"])

        insult = " ".join(first_word, second_word, third_word)

        prefix = user + ", " if user else ""
        return prefix + "thou " + insult + "!"

classes = (Insult,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
