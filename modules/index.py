# @File        : index.py
# @Description :
# @Time        : 04 March, 2021
# @Author      : Cyan
import configparser
import json
import re
import sqlite3
from datetime import datetime
from porter2stemmer import Porter2Stemmer


class Posting:
    rid = 0  # recipe id
    tf = 0  # term frequency
    length = 0  # length of the content

    def __init__(self, rid, tf, length):
        self.rid = rid
        self.tf = tf
        self.length = length

    def __repr__(self):
        return str(self.rid) + '\t' + str(self.tf) + '\t' + str(self.length)

    def __str__(self):
        return str(self.rid) + '\t' + str(self.tf) + '\t' + str(self.length)


class IndexModule:
    data_list = None
    data_n = None

    stop_words = set()  # set of stop words
    stemmer = Porter2Stemmer()  # init porter stemmer

    config_path = None
    config = None

    def __init__(self):
        """
        init config, stop words, data list
        """
        self.config_path = 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path, 'utf-8')

        with open(self.config['DEFAULT']['STOPWORDS_PATH'], encoding='utf-8') as f:
            self.stop_words = set(f.read().split())

        with open(self.config['DEFAULT']['RECIPES_PATH'], encoding='utf-8') as f:
            self.data_list = f.read().split('\n')
            self.data_n = len(self.data_list)

        # write DATA_N to config
        self.config.set('DEFAULT', 'DATA_N', str(self.data_n))
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def write_index_to_db(self, index, table_name):
        """
        write inverted index to db
        index in form of # form: {term: [df, [posting, ...]], ...}
        :param table_name:
        :param index:
        :return:
        """
        conn = sqlite3.connect(self.config['DEFAULT']['SE_DB_PATH'])
        c = conn.cursor()

        c.execute('drop table if exists %s' % table_name)
        c.execute('create table %s (term text primary key, df integer, postings text)' % table_name)

        for key, value in index.items():
            posting_list = '\n'.join(map(str, value[1]))
            values = (key, value[0], posting_list)
            c.execute('insert into %s values (?, ?, ?)' % table_name, values)

        conn.commit()
        conn.close()

    def data_cleanup_tf(self, data):
        """
        clean data and construct tf dictionary
        :param data:
        :return: length of data and tf dictionary
        """
        tf_dict = {}  # {term: tf, ...}
        n = 0  # length of data

        terms = data.lower().split()  # lower the data and split
        for term in terms:
            # filter stop words having quotation marks
            # filter sites in a simple way
            if (term not in self.stop_words) and ('http' not in term) and ('www' not in term):
                term = re.sub(r'[^a-z]', '', term)  # remove non-alphabetic letters
                # filter stop words again and blank term
                if (term not in self.stop_words) and (len(term) != 0):
                    term = self.stemmer.stem(term)  # stemming
                    n += 1
                    if term in tf_dict:
                        tf_dict[term] += 1
                    else:
                        tf_dict[term] = 1
        return n, tf_dict

    def construct_index_name_desc(self):
        """
        construct inverted index with name and description
        :return:
        """
        inverted_index = {}  # form: {term: [df, [posting, ...]], ...}
        AVG_LEN = 0  # average length for name and description

        for x in self.data_list:
            recipe = json.loads(x)
            rid = recipe['id']
            name = recipe['name']
            description = recipe['description']

            length, term_tf = self.data_cleanup_tf(name + ' ' + description)
            AVG_LEN += length
            for term, tf in term_tf.items():
                posting = Posting(rid, tf, length)
                if term in inverted_index:
                    inverted_index[term][0] += 1  # df++
                    inverted_index[term][1].append(posting)  # add posting to list
                else:
                    inverted_index[term] = [1, [posting]]  # [df, [posting]]

        AVG_LEN /= self.data_n
        # print(len(inverted_index), inverted_index)

        # write AVG_LEN to config
        self.config.set('DEFAULT', 'AVG_LEN', str(AVG_LEN))
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

        self.write_index_to_db(inverted_index, 'index_name_desc')

    def construct_index_name(self):
        """
        construct inverted index with name
        :return:
        """
        inverted_index = {}  # form: {term: [df, [posting, ...]], ...}

        for x in self.data_list:
            recipe = json.loads(x)
            rid = recipe['id']
            name = recipe['name']

            length, term_tf = self.data_cleanup_tf(name)
            for term, tf in term_tf.items():
                posting = Posting(rid, tf, length)
                if term in inverted_index:
                    inverted_index[term][0] += 1  # df++
                    inverted_index[term][1].append(posting)  # add posting to list
                else:
                    inverted_index[term] = [1, [posting]]  # [df, [posting]]
        # print(len(inverted_index), inverted_index)

        self.write_index_to_db(inverted_index, 'index_name')

    def construct_index_ingredient(self):
        """
        construct inverted index with ingredient
        :return:
        """
        inverted_index = {}  # form: {term: [df, [posting, ...]], ...}

        for x in self.data_list:
            recipe = json.loads(x)
            rid = recipe['id']
            ing = recipe['ingredients']

            length, term_tf = self.data_cleanup_tf(ing)
            for term, tf in term_tf.items():
                posting = Posting(rid, tf, length)
                if term in inverted_index:
                    inverted_index[term][0] += 1  # df++
                    inverted_index[term][1].append(posting)  # add posting to list
                else:
                    inverted_index[term] = [1, [posting]]  # [df, [posting]]

        self.write_index_to_db(inverted_index, 'index_ingredient')


if __name__ == '__main__':
    print('-----start time: %s-----' % (datetime.today()))
    im = IndexModule()
    im.construct_index_name_desc()
    im.construct_index_name()
    im.construct_index_ingredient()
    print('-----finish time: %s-----' % (datetime.today()))
