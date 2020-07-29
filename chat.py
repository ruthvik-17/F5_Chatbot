import random
from constants import *

class chat_bot():
    # All other functioalities are called from here.

    def __init__(self):
        self.state = 0

    def greet(self):
        if self.state == 0:
            print(random.choice(GREETING_PHRASE_1) + random.choice(GREETING_PHRASE_2))
            self.state = 1
        pass

    def funcname(self):
        pass