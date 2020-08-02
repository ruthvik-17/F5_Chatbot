import random
import importlib
from constants import GREETING_PHRASE_1, GREETING_PHRASE_2


class ChatBot:
    # All other functionalities are defined/called in this class.

    def __init__(self):
        self.state = 0

    def greet(self):
        print(random.choice(GREETING_PHRASE_1) + random.choice(GREETING_PHRASE_2))
        self.state = 1

    def start_chat(self):
        if self.state == 0:
            self.greet()
