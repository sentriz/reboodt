from plugins.__init__ import BaseCommand
import random
import os

class EightBall(BaseCommand):
    """
    reboodt plugin, magic 8 ball
    usage: .8 question
    result: positive/negative/neutral
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = ".8"
        self.replies = {}

        self._load_replies()

    def _load_replies(self):
        current_folder = os.path.dirname(__file__)
        provisional_path = os.path.join(current_folder, os.pardir)
        parent_folder = os.path.abspath(provisional_path)
        replies_file = os.path.join(parent_folder, "files", "8ball_replies.txt")

        with open(replies_file) as file:
            for line in file:
                line = line.rstrip()
                if line.startswith("#"):
                    continue
                self.replies.append(line)

    def command_function(self, arguments, sender, channel):
        question = " ".join(arguments)
        if not question:
            return "Cannot predict now. Try providing a question."
            
        reply = random.choice(self.replies)
        
        return reply

classes = (EightBall,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
