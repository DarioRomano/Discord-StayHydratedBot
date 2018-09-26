import datetime


class UserData:
    """A class used for managing timers and preferences of users"""
    def __init__(self, guild=None, channel=None):
        self.dm = True
        self.pause = False
        self.drink_break = datetime.timedelta(seconds=3600)
        self.last_drink = datetime.datetime.now()
        self.total = 0
        self.guild = guild
        self.channel = channel
        self.reminded = False

    def can_dm(self):
        return self.dm

    def paused(self):
        return self.pause

    def next_drink(self):
        return self.last_drink + self.drink_break

    def drink(self):
        self.last_drink = datetime.datetime.now()
        self.total += 1
        self.reminded = False

    def toggle_dm(self):
        self.dm = not self.dm

    def toggle_pause(self):
        self.pause = not self.pause

    def should_drink(self):
        return datetime.datetime.now() >= self.next_drink()

    def times_drunk(self):
        return self.total

    def set_break(self, time):
        self.drink_break = time

    def update_channel(self, guild, channel):
        self.guild = guild
        self.channel = channel

    def was_reminded(self):
        return self.reminded

    def remind(self):
        self.reminded = True
