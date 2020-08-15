import math
import re
# import time
# from typing import Dict, List
import nltk

try:
    from nltk.corpus import stopwords
except LookupError:
    nltk.download("stopwords")
    from nltk.corpus import stopwords


def clean_text_tokens(text):
    text = re.sub(r'[\'\"\n?]', '', text)
    text = re.sub(r'[.\s]', r' ', text)
    tokens = re.split(r'[^a-zA-Z0-9.\-]', text.lower())
    return tokens


def remove_stopwords(tokens):
    sw = stopwords.words('english')
    for each in sw:
        if re.search(r"\'", each):
            sw.remove(each)
            sw.append(re.sub(r"\'", r'', each))
    for each in sw:
        if each in tokens:
            tokens.remove(each)


def generate_results_t2(tfidf, query_tfidf):
    rank_map_t2 = {}
    j = 0
    for tfidf_row in tfidf:
        sum_val = 0
        tfidf_row_square = 0
        tfidf_query_square = 0
        # print("check")
        for i in range(0, len(tfidf_row)):
            sum_val = sum_val + tfidf_row[i] * query_tfidf[i]
            tfidf_row_square = tfidf_row_square + tfidf_row[i] * tfidf_row[i]
            tfidf_query_square = tfidf_query_square + query_tfidf[i] * query_tfidf[i]
        bottom = math.sqrt(tfidf_row_square * tfidf_query_square)
        if bottom == 0:
            bottom = 1
        rank_map_t2[j] = sum_val / bottom
        j += 1
    return sorted(rank_map_t2.items(), key=lambda x: x[1], reverse=True)


class Detection:
    def __init__(self, answers, detection_type):
        """
        Detects intent/answer for a given sentence.
        :param answers: List[Tuple(str(question), str(answer))]
        detection_type: str 'intent'/'answer'
        """
        self.type = detection_type.lower()
        self.total_count = 0
        self.index_map = {}
        self.word_map = {}
        self.k = answers
        # for each in answers:
        #     for i in each:
        #         self.k.append((i['question'], i['answer']))

        # k = re.findall(r'\$\$\s*(.*)\n\^\^\s*(.*)', data_file)

        self.data_len = len(self.k)

        self.process_data(self.k)

        self.remove_stop_words()

        self.build_inverted_index(self.k)

        top_tuple = sorted(self.word_map.items(), key=lambda x: x[1], reverse=True)
        top_words = []
        self.position_map = {}
        self.matrix_size = len(self.word_map) if len(self.word_map) < 1000 else 1000
        for i in range(self.matrix_size):
            key_word = top_tuple[i][0]
            top_words.append(key_word)
            self.position_map[key_word] = int(i)

        self.tfidf = self.generate_tfidf(self.k, self.position_map, self.matrix_size)

        # check = True
        # while check:
        #     query = input("please enter your search query...")
        #     self.process_results(query, self.matrix_size)
        #     con = input("Do you want to continue : Y/N ?....")
        #     if con == "n" or con == "N":
        #         check = False

    def add_to_map(self, data_tokens):
        # global total_count
        # data_tokens = re.split(r'[^a-zA-Z0-9\']', this_data)
        for word in data_tokens:
            if len(word) > 0:
                if word in self.word_map:
                    val = self.word_map[word]
                    self.word_map[word] = val + 1
                    self.total_count += 1
                else:
                    self.word_map[word] = 1
                    self.total_count += 1

    def process_data(self, data):
        # global total_count

        for each in data:
            # add questions and answers to word_map
            if self.type == 'answer':
                self.add_to_map(clean_text_tokens(each[0]) + clean_text_tokens(each[1]))
            else:
                self.add_to_map(clean_text_tokens(each[0]))

    def remove_stop_words(self):
        # global total_count
        sw = stopwords.words('english')
        for each in sw:
            if re.search(r"\'", each):
                sw.remove(each)
                sw.append(re.sub(r"\'", r'', each))
        for each in sw:
            if each in self.word_map:
                val = self.word_map[each]
                self.total_count = self.total_count - val
                del (self.word_map[each])

    def build_inverted_index(self, data):
        for idx in range(len(data)):
            q_tokens = clean_text_tokens(data[idx][0])
            a_tokens = clean_text_tokens(str(data[idx][1]))
            if self.type == 'answer':
                tokens = q_tokens + q_tokens + a_tokens
            else:
                tokens = q_tokens

            for word in tokens:
                if word in self.word_map:
                    if word in self.index_map:
                        val = self.index_map[word]
                        if idx in val:
                            count = val[idx] + 1
                            val[idx] = count
                        else:
                            val[idx] = 1
                        self.index_map[word] = val
                    else:
                        val = {idx: 1}
                        self.index_map[word] = val

    def generate_tfidf(self, data, position_map: {str: [int]}, size):
        tfidf = [[0] * size for n in range(len(data))]
        i = int(-1)
        for idx in range(len(data)):
            i += 1
            if self.type == "answer":
                q_tokens = clean_text_tokens(data[idx][0])
                a_tokens = clean_text_tokens(data[idx][1])

                this_data = re.sub(r'[\'\"\n]', '', data[idx][0] + " " + data[idx][0] + " " + data[idx][1])
                this_data = re.sub(r'\.\s', r' ', this_data.lower())

                tokens = q_tokens + q_tokens + a_tokens
            else:
                q_tokens = clean_text_tokens(data[idx][0])

                this_data = re.sub(r'[\'\"\n]', '', data[idx][0])
                this_data = re.sub(r'\.\s', r' ', this_data.lower())

                tokens = q_tokens
            # sw = stopwords.words('english')
            # for each in sw:
            #     if re.search(r"\'", each):
            #         sw.remove(each)
            #         sw.append(re.sub(r"\'", r'', each))
            # for each in sw:
            #     if each in tokens:
            #         tokens.remove(each)

            remove_stopwords(tokens)

            for word in tokens:
                if word in position_map:
                    count_word = this_data.count(word)
                    tf = count_word / len(tokens)
                    idf = math.log(len(data) / len(self.index_map[word]), 10)
                    tfidf[i][position_map[word]] = tf * idf
        # with open("tfidf.txt", 'a') as out:
        #     out.write(str(tfidf))
        return tfidf

    def transform_query_tfidf(self, query, position_map, size):
        query_tfidf = [0] * size
        # token_query = query.split(' ')
        token_query = clean_text_tokens(query)
        # sw = stopwords.words('english')
        # for each in sw:
        #     if re.search(r"\'", each):
        #         sw.remove(each)
        #         sw.append(re.sub(r"\'", r'', each))
        # for each in sw:
        #     if each in token_query:
        #         token_query.remove(each)

        remove_stopwords(token_query)

        for word in token_query:
            if word in position_map:
                count_word = query.count(word)
                tf = count_word / len(token_query)
                idf = math.log(self.data_len / len(self.index_map[word]), 10)
                query_tfidf[position_map[word]] = tf * idf
        return query_tfidf

    def process_results(self, query):
        query_tfidf = self.transform_query_tfidf(query, self.position_map, self.matrix_size)
        # start_time = time.time()
        result_2 = generate_results_t2(self.tfidf, query_tfidf)
        original_length_2 = 0
        for val in result_2:
            if val[1] > 0:
                original_length_2 += 1

        if self.type == 'answer':
            if original_length_2 > 0:
                return self.k[result_2[0][0]][0], self.k[result_2[0][0]][1], result_2[0][1]
            else:
                return "", False, 0
        else:
            if original_length_2 > 0:
                return self.k[result_2[0][0]][1]
            else:
                return 0
                # print("Results")
        # print("*************")
        # if len(result_2) > 4:
        #     result_2 = result_2[0:4]
        # i = 1
        # if original_length_2 == 0:
        #     print("No result found :(")
        # for val in result_2:
        #     rank = val[0] + 1
        #     if val[1] > 0.0:
        #         print("Question: " + self.k[rank - 1][0])
        #         print("Answer: " + self.k[rank - 1][1])
        #         print("Rank-" + str(i) + ": doc " + str(rank) + " : " + str(val[1]))
        #     i += 1
        # print("---------------")
        # print("Total number of related documents " + str(original_length_2))
        # print("---------------")
