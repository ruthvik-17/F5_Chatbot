import random
import re
import pickle

import pandas as pd
# import numpy as np
# import re
from constants import GREETING_PHRASE_1, GREETING_PHRASE_2, STOP_CHAT, INTENT_DATA
from detection import Detection


def clean_text(text):
    text = re.sub(r'[\'\"\n?]', '', text)
    text = re.sub(r'[.\s]', r' ', text.lower())
    return text


class ChatBot:
    # All other functionalities are defined/called in this class.

    def __init__(self):
        self.state = 0
        self.exit = False
        self.curr_msg = None
        self.menu = {}
        self.create_menu_graph()
        # print(self.menu)

        pk_file = open('k_.pkl', 'rb')
        answers = pickle.load(pk_file)
        self.answer_detector = Detection(answers=answers, detection_type='answer')

        intent_answers = []
        for each in INTENT_DATA:
            for i in INTENT_DATA[each]['data']:
                intent_answers.append((clean_text(i), INTENT_DATA[each]['number']))
        self.intent_detector = Detection(answers=intent_answers, detection_type='intent')

    def greet(self):
        print(random.choice(GREETING_PHRASE_1) + random.choice(GREETING_PHRASE_2))
        self.state = 1

    def create_menu_graph(self):
        data = pd.read_csv("menu.csv", index_col=0, header=0, encoding='utf-8')
        for row_idx, row in data.iterrows():
            # print(row_idx, row['subsections'] if pd.notna(row['subsections']) else False)
            self.menu[int(row_idx)] = {'name': '', 'subsections': [], 'data': []}
            if pd.notna(row['name']):
                self.menu[int(row_idx)]['name'] = row['name']
            if pd.notna(row['subsections']):
                self.menu[int(row_idx)]['subsections'] = row['subsections'].split('|')
            if pd.notna(row['data']):
                self.menu[int(row_idx)]['data'] = row['data'].split('|')

    def detect_intent(self, query):
        intent = self.intent_detector.process_results(query)
        # print("\n\n detected intent:", intent, "\n\n")
        return intent

    def detect_answer(self, query):
        question, answer, score = self.answer_detector.process_results(query)
        # print("question:", question, "\n detected  answer:", answer, ", score:", score)
        if score > 0.7:
            return answer
        else:
            return False

    def handle_sales(self):
        print("Would you like to get in touch with the F5 team to "
              "discover what would be a good fit for your specific use case?")
        print("You can type yes/no.")
        response = input("user: ")
        if response.strip(r'.').lower() in ['yes', 'okay', 'sure']:
            print("Okay, please provide your work e-mail id.")
            email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', input("user: "))
            if email:
                # self.send_mail(email)
                print("Mail noted. Our sales executive will contact you.")
            else:
                print("Email not found.")
        print("\nOkay. Back to main menu.")
        self.handle_intent(INTENT_DATA['Main menu']['number'])

    def handle_intent(self, intent_num):
        """

        :return:
        """

        data = self.menu[intent_num]['data']
        sub_sections = self.menu[intent_num]['subsections']
        if data:
            for each in data:
                print("\n", each.strip())
        if sub_sections:
            for each in sub_sections:
                print("->" + self.menu[int(each.strip())]['name'])
        else:
            self.handle_sales()

    def start_chat(self):
        if self.state == 0:
            self.greet()

        while not self.exit:
            text = input("user:")
            # text = re.sub(r'[\'\"\n?]', '', text)
            # text = re.sub(r'[\.\s]', r' ', text.lower())
            self.curr_msg = clean_text(text).strip()
            if self.curr_msg not in STOP_CHAT:
                intent = self.detect_intent(self.curr_msg)
                answer = self.detect_answer(self.curr_msg)
                if answer and intent:
                    print("\n" + answer)
                    self.handle_intent(intent)
                elif answer:
                    print("\n" + str(answer))
                    self.handle_intent(INTENT_DATA['Main menu']['number'])
                elif intent:
                    self.handle_intent(intent)
                else:
                    self.handle_intent(INTENT_DATA['Main menu']['number'])
            else:
                self.exit = True
        print("Good bye.")
