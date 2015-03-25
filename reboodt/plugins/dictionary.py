from plugins.__init__ import BaseCommand

class MerriamWebster(BaseCommand):
    """
    reboodt plugin that defines a given word
    usage: .define word
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = ".define"

    def command_function(self, arguments, sender, channel):
        pass

classes = (Dict,)

if __name__ == "__main__":
    for class_ in classes:
        print(class_.__doc__)
