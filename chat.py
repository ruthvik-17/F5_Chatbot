import random
import re
import pickle

import pandas as pd
# import numpy as np
# import re
from constants import GREETING_PHRASE_1, GREETING_PHRASE_2, STOP_CHAT, INTENT_DATA
from detection import Detection


def clean_text(text):
    text = re.sub(r'[\'\"?]', '', text)
    text = re.sub(r'[.\s?]', r' ', text.lower())
    return text


class ChatBot:
    # All other functionalities are defined/called in this class.

    def __init__(self):
        # self.state = 'start'
        self.state = 'intent'
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
        self.state = 'intent'
        return random.choice(GREETING_PHRASE_1) + random.choice(GREETING_PHRASE_2)

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
        # print(" detected intent:", intent, "")
        return intent

    def detect_answer(self, query):
        question, answer, score = self.answer_detector.process_results(query)
        # print("question:", question, " detected  answer:", answer, ", score:", score)
        if score > 0.7:
            return answer
        else:
            return False

    def handle_sales(self, text):
        # print("Would you like to get in touch with the F5 team to "
        #       "discover what would be a good fit for your specific use case?")
        # print("You can type yes/no.")
        # response = input("user: ")
        response = text
        result = []
        if self.state == "sales":
            if response.strip(r'.').lower() in ['yes', 'okay', 'sure']:
                # print("Okay, please provide your work e-mail id.")
                result.append(("Okay, please provide your work e-mail id.", "text"))
                self.state = "get_mail"
                return result
        elif self.state == "get_mail":
            email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', response)
            self.state = "intent"
            if email:
                # self.send_mail(email)
                # print("Mail noted. Our sales executive will contact you.")
                result.append(("Mail noted. Our sales executive will contact you.", "text"))
            else:
                # print("Email not found.")
                result.append(("Email not found.", "text"))
        # result.append(("Okay. Back to main menu.", "text"))
        # print("Okay. Back to main menu.")
        self.state = 'intent'
        result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
        return result

    def handle_intent(self, intent_num):
        """

        :return:
        """

        data = self.menu[intent_num]['data']
        sub_sections = self.menu[intent_num]['subsections']
        result = []
        if data:
            for each in data:
                # result += each.strip() + ""
                result.append((each.strip(), 'text'))
                # print("", each.strip())

        if sub_sections:
            for each in sub_sections:
                # result += "->" + self.menu[int(each.strip())]['name']
                result.append((self.menu[int(each.strip())]['name'], 'button'))
        else:
            # result += "Would you like to get in touch with the F5 team to " \
            #           "discover what would be a good fit for your specific use case?" + "" + "You can type yes/no."
            result.append(("Would you like to get in touch with the F5 team to "
                           "discover what would be a good fit for your specific use case?", 'text'))
            result.append(('Yes!', 'button'))
            result.append(('No.', 'button'))

            self.state = "sales"
        return result

    def get_response(self, text):
        # if self.state == 0:
        #     self.greet()
        self.curr_msg = clean_text(text).strip()
        result = []
        if self.state == "intent":
            if not self.exit:
                # text = input("user:")
                # text = re.sub(r'[\'\"?]', '', text)
                # text = re.sub(r'[\.\s]', r' ', text.lower())
                if self.curr_msg not in STOP_CHAT:
                    intent = self.detect_intent(self.curr_msg)
                    answer = self.detect_answer(self.curr_msg)
                    if answer and intent:
                        # print("" + answer)
                        result.append((answer, 'text'))
                        result.extend(self.handle_intent(intent))
                    elif answer:
                        # print("" + str(answer))
                        # result += self.handle_intent(INTENT_DATA['Main menu']['number'])
                        result.append((answer, 'text'))
                        result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
                    elif intent:
                        # result += self.handle_intent(intent)
                        result.extend(self.handle_intent(intent))
                    else:
                        result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
                        # result += self.handle_intent(INTENT_DATA['Main menu']['number'])
                else:
                    self.exit = True
        elif self.state == "sales":
            result.extend(self.handle_sales(self.curr_msg))
            # result += self.handle_sales(self.curr_msg)
        elif self.state == "get_mail":
            result.extend(self.handle_sales(text))
            # result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
            # result += self.handle_sales(text)
            # result += self.handle_intent(INTENT_DATA['Main menu']['number'])
        if self.exit:
            self.exit = False
            return [("Good bye.", "text")]

        return result
