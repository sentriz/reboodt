from files.plugins.__init__ import BaseVariable
from datetime import datetime

class Time(BaseVariable):
    """
    reboodt variable, returns the current time
    usage: .time
    returns: yyyy/mm/dd hh:mm:ss
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = ".time"

    def variable_function(self):
        time_format = "%Y/%m/%d %H:%M:%S"
        current_time = datetime.now()
        time_string = current_time.strftime(time_format)
        return time_string

class Last(BaseVariable):
    """
    reboodt variable, returns the last message of the channel
    usage: .last
    returns: this message if someone said this message if som..
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = ".last"

    def variable_function(self):
        last_message = self.bot.last_message
        if last_message:
            return last_message
        else:
            return "could not find last message"

classes = (Time, Last)

if __name__ == "__main__":
    for variable in variables:
        print(variable.__doc__)
