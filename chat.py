import json
import pickle
import random
import re
import smtplib
import ssl
from itertools import combinations

import pandas as pd
from nltk import ngrams
from spello.model import SpellCorrectionModel

from constants import GREETING_PHRASE_1, GREETING_PHRASE_2, STOP_CHAT, INTENT_DATA
from detection import Detection


def clean_text(text):
    text = re.sub(r'[\'\"?]', '', text)
    text = re.sub(r'[.\s?]', r' ', text.lower())
    return text


def get_ngrams(tokens, n):
    return list(ngrams(tokens, n))


def get_context_pairs(tokens, word):
    """
    For given list of tokens and word, return all pairs possible within window of 4 words of the given word,
    ignore single letter word.
    Args:
        tokens (list): list of tokens
        word (str): word for which we are searching for tokens
    Returns:
        (list): list of pairs with the given word in it
    Examples:
        >>> tokens, 'f5'
        >>> get_context_pairs(['This', 'is', 'f5', 'networks', 'inc'])
        [('This', 'f5'),
         ('f5', 'inc'),
         ('f5', 'networks'),
         ('is', 'f5')]
    """
    data = []
    n_grams = get_ngrams(tokens, 4)
    if not n_grams:
        n_grams = [tokens]
    for ngrams_batch in n_grams:
        for pair in combinations(ngrams_batch, 2):
            # diff_index = abs(tokens.index(pair[0]) - abs(tokens.index(pair[1])))
            if len(pair[0]) < 2 or len(pair[1]) < 2:
                continue
            if pair[0] == word or pair[1] == word:
                data.append(pair)
    return data


class ChatBot:
    # All other functionalities are defined/called in this class.

    def __init__(self):
        # self.state = 'start'
        self.state = 'intent'
        self.exit = False
        self.curr_msg = None
        self.menu = {}
        self.create_menu_graph()
        self.browser = 'chrome'
        # print(self.menu)
        self.spell_check_model = SpellCorrectionModel(language='en')
        self.domain_spell_check_model = SpellCorrectionModel(language='en')
        self.spell_check_model.load('en.pkl')
        self.domain_spell_check_model.load('custom_model.pkl')
        with open('data.json', "r") as f:
            self.db = json.load(f)
        f.close()
        # with open('words.json') as f:
        #     self.all_words = json.load(f)
        # f.close()

        pk_file = open('final.pkl', 'rb')
        answers = pickle.load(pk_file)
        self.answer_detector = Detection(answers=answers, detection_type='answer')

        intent_answers = []
        for each in INTENT_DATA:
            for i in INTENT_DATA[each]['data']:
                intent_answers.append((clean_text(i), INTENT_DATA[each]['number']))
        self.intent_detector = Detection(answers=intent_answers, detection_type='intent')

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        self.sender_email = "f5.demochatcustomer@gmail.com"
        self.receiver_email = "f5.demochatsup@gmail.com"
        password = "ruthvik@sl"
        context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(smtp_server, port, context=context)
        self.server.login(self.sender_email, password)

    def greet(self):
        self.state = 'intent'
        result = []
        if self.db[self.browser]["name"]:
            greet_msg = "Hello " + self.db[self.browser]["name"] + "! What brings you back?"
        else:
            greet_msg = random.choice(GREETING_PHRASE_1) + " " + random.choice(GREETING_PHRASE_2)
        result.append((greet_msg, "text"))
        return result

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
        #  detect answer from a given question
        question, answer, score = self.answer_detector.process_results(query)
        # print("question:", question, " detected  answer:", answer, ", score:", score)
        if score > 0.7:
            return "<strong>Answer: </strong>" + answer.capitalize()
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
                if self.db[self.browser]["email"] and self.db[self.browser]["name"]:
                    result.append(("Customer email id and name are already present.", "text"))
                    result.append(("Please provide a summary of your "
                                   "requirement for our executive to have some context beforehand.", "text"))
                    self.state = "get_summary"
                    return result
                elif self.db[self.browser]["email"]:
                    self.state = "get_name"
                    result.append(("Customer email id is already in our database.", "text"))
                    return result.append(("Please provide you name.", "text"))
                # print("Okay, please provide your work e-mail id.")
                result.append(("Please provide your work e-mail id.", "text"))
                self.state = "get_mail"
                return result
        elif self.state == "get_mail":
            email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', response)

            if email:
                # self.send_mail(email)
                # print("Mail noted. Our sales executive will contact you.")
                self.add_to_db(email[0], "email")
                self.state = "get_name"
                if self.db[self.browser]["name"]:
                    result.append(("Mail noted and Name is present in our database.", "text"))
                    result.append(("Last thing, please provide a summary of your "
                                   "requirement for our executive to have some context beforehand.", "text"))
                else:
                    result.append(("Mail noted. Please provide your name.", "text"))
                return result
            else:
                # self.state = "intent"
                # print("Email not found.")
                return result.append(("Email not found. Lets try that again.", "text"))
        elif self.state == "get_name":
            name = response
            if name:
                # self.send_mail(email)
                # print("Mail noted. Our sales executive will contact you.")
                self.add_to_db(name, "name")
                result.append(("Name noted. Last thing, please provide a summary of your "
                               "requirement for our executive to have some context beforehand.", "text"))
                self.state = "get_summary"
                return result
            else:
                # print("Email not found.")
                return result.append(("Name not found.", "text"))
        elif self.state == "get_summary":
            summary = response
            self.state = "intent"
            if summary:
                # self.send_mail(email)
                # print("Mail noted. Our sales executive will contact you.")
                # self.add_to_db(summa, "name")
                if self.send_mail(summary):
                    result.append(("Summary noted. Our executive has been notified and "
                                   "will contact you soon. Thank you.", "text"))
                # send email to support staff
            else:
                # print("Email not found.")
                result.append(("Summary not found.", "text"))
        # result.append(("Okay. Back to main menu.", "text"))
        # print("Okay. Back to main menu.")
        self.state = 'intent'
        result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
        return result

    def send_mail(self, summary):

        message = f"""\
        Subject: Customer ticket #147007.


        We got the following customer ticket through our website chatbot. Please look in to it.

        Name: {self.db[self.browser]["name"] if self.db[self.browser]["name"] else "Not provided"}
        email: {self.db[self.browser]["email"]}
        Summary: {summary}

        Thanks and regards,
        Chatbot team.
        """
        # context = ssl.create_default_context()
        # with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        #     server.login(sender_email, password)
        try:
            self.server.sendmail(self.sender_email, self.receiver_email, message)
        except:
            port = 465  # For SSL
            smtp_server = "smtp.gmail.com"
            self.sender_email = "f5.demochatcustomer@gmail.com"
            self.receiver_email = "f5.demochatsup@gmail.com"
            password = "ruthvik@sl"
            context = ssl.create_default_context()
            self.server = smtplib.SMTP_SSL(smtp_server, port, context=context)
            self.server.login(self.sender_email, password)
            self.server.sendmail(self.sender_email, self.receiver_email, message)
        return True

    def get_order(self, sub_sections):
        with open('data.json', "r") as f:
            data = json.load(f)
        f.close()
        counts = {}
        if self.browser in data:
            # print(data)
            for each in sub_sections:
                intent = each.strip()
                if intent in data[self.browser]["history"]:
                    counts[intent] = data[self.browser]["history"][intent]
                else:
                    counts[intent] = 0
        order = []
        for i in sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
            order.append(int(i[0]))
        return order

    def add_to_db(self, command_data, command):
        with open('data.json', "r") as f:
            self.db = json.load(f)
        f.close()

        file = open("data.json", "r+")
        file.truncate(0)
        file.close()

        command_data = str(command_data).strip()
        if command == "intent":
            if self.browser in self.db:
                if command_data in self.db[self.browser]["history"]:
                    x = self.db[self.browser]["history"][command_data]
                    self.db[self.browser]["history"][command_data] = x + 1
                    # print("x:", x)
                    # print("updated data:", self.db)
                else:
                    self.db[self.browser]["history"][command_data] = 1
            else:
                self.db[self.browser] = {"history": {}, "name": "", "email": ""}
                self.db[self.browser]["history"][command_data] = 1

        elif command == "name":
            self.db[self.browser]["name"] = command_data
        elif command == "email":
            self.db[self.browser]["email"] = command_data

        with open('data.json', "w") as a:
            json.dump(self.db, a)
        a.close()

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
            order = self.get_order(sub_sections)
            if order:
                for i in order:
                    result.append((self.menu[i]['name'], 'button'))
            else:
                for each in sub_sections:
                    # result += "->" + self.menu[int(each.strip())]['name']
                    result.append((self.menu[int(each.strip())]['name'], 'button'))
        else:
            # result += "Would you like to get in touch with the F5 team to " \
            #           "discover what would be a good fit for your specific use case?" + "" + "You can type yes/no."
            result.append(("Would you like to get in touch with the F5 team to "
                           "discover what would be a good fit for your specific use case?", 'text'))
            result.append(('Yes', 'button'))
            result.append(('No', 'button'))

            self.state = "sales"
        return result

    def check_domain_context(self, sentence, word):
        pairs_list = get_context_pairs(sentence.lower().split(), word)
        for each in pairs_list:
            a = each in self.domain_spell_check_model.context_model.model_dict
            b = (each[1], each[0]) in self.domain_spell_check_model.context_model.model_dict
            if a or b:
                return True
        return False

    def spell_check(self, text):
        response = ""
        final_suggestions_dict = {}
        global_response = self.spell_check_model.spell_correct(text)
        domain_response = self.domain_spell_check_model.spell_correct(text)
        # print("Global_response", global_response)
        # print("domain_response", domain_response)
        for each in global_response['correction_dict']:
            # if each in self.all_words:
            #     continue
            if each in domain_response['correction_dict']:
                corrected_domain_each = domain_response['correction_dict'][each]
                if self.check_domain_context(domain_response['spell_corrected_text'], corrected_domain_each):
                    final_suggestions_dict[each] = corrected_domain_each
                else:
                    final_suggestions_dict[each] = global_response['correction_dict'][each]
            # else:
            #     final_suggestions_dict[each] = global_response['correction_dict'][each]
        for each in global_response['original_text'].split():
            if each in final_suggestions_dict:
                response += final_suggestions_dict[each] + ' '
            else:
                response += each + ' '
        return response.strip()

    def initialize(self, browser):
        self.browser = browser
        if self.browser not in self.db:
            self.db[self.browser] = {"history": {}, "name": "", "email": ""}
        with open('data.json', "w") as a:
            json.dump(self.db, a)
        a.close()

    def get_response(self, text, browser, command):
        # if self.state == 0:
        #     self.greet()
        result = []
        if command == "start":
            result.extend(self.greet())
        else:
            self.browser = browser
            self.curr_msg = self.spell_check(text)
            self.curr_msg = clean_text(self.curr_msg)
            if self.curr_msg not in STOP_CHAT:
                if self.state == "intent":
                    if not self.exit:
                        # text = input("user:")
                        # text = re.sub(r'[\'\"?]', '', text)
                        # text = re.sub(r'[\.\s]', r' ', text.lower())
                        # if self.curr_msg not in STOP_CHAT:
                        intent = self.detect_intent(self.curr_msg)
                        answer = self.detect_answer(self.curr_msg)
                        if intent == 6:
                            # support request
                            result.append(("A support assistant will contact you soon.", "text"))
                            self.state = "sales"
                            result.extend(self.handle_sales("yes"))
                        elif answer and intent:
                            # print("" + answer)
                            self.add_to_db(intent, "intent")
                            result.append((answer + '.', 'text'))
                            result.extend(self.handle_intent(intent))
                        elif answer:
                            # print("" + str(answer))
                            # result += self.handle_intent(INTENT_DATA['Main menu']['number'])
                            result.append((answer + '.', 'text'))
                            result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
                        elif intent:
                            self.add_to_db(intent, "intent")
                            # result += self.handle_intent(intent)
                            result.extend(self.handle_intent(intent))
                        else:
                            result.append(("Sorry, I did not understand that.", "text"))
                            result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
                            # result += self.handle_intent(INTENT_DATA['Main menu']['number'])
                elif self.state == "sales":
                    result.extend(self.handle_sales(self.curr_msg))
                    # result += self.handle_sales(self.curr_msg)
                elif self.state == "get_mail":
                    result.extend(self.handle_sales(text))
                    # result.extend(self.handle_intent(INTENT_DATA['Main menu']['number']))
                    # result += self.handle_sales(text)
                    # result += self.handle_intent(INTENT_DATA['Main menu']['number'])
                elif self.state == "get_name":
                    result.extend(self.handle_sales(text))
                elif self.state == "get_summary":
                    result.extend(self.handle_sales(text))
            else:
                self.exit = True

            if self.exit:
                self.exit = False
                return [("Good bye.", "text")]

        return result
