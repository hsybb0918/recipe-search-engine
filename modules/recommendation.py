# @File        : recommendation.py
# @Description :
# @Time        : 04 March, 2021
# @Author      : Cyan
import configparser
import re
import sqlite3

from datetime import datetime
from porter2stemmer import Porter2Stemmer
from scipy.sparse import dok_matrix
from sklearn.neighbors import NearestNeighbors


class RecommendationModule:
    data_list = None
    data_n = None
    cleaned_data_list = []

    vocab = set()

    stop_words = set()  # set of stop words
    stemmer = Porter2Stemmer()  # init porter stemmer

    config_path = None
    config = None

    conn = None

    def __init__(self):
        """
        init config, stop words, data list, database
        """
        self.config_path = 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path, 'utf-8')

        with open(self.config['DEFAULT']['STOPWORDS_PATH'], encoding='utf-8') as f:
            self.stop_words = set(f.read().split())

        self.conn = sqlite3.connect(self.config['DEFAULT']['SE_DB_PATH'])
        self.conn.row_factory = sqlite3.Row
        c = self.conn.cursor()
        self.data_list = c.execute('select * from recipes').fetchall()
        self.data_n = len(self.data_list)

        c.execute('drop table if exists k_nearest')
        c.execute('create table k_nearest (id integer primary key, '
                  'nn1 integer, nn2 integer, nn3 integer, nn4 integer, nn5 integer)')
        self.conn.commit()

    def __del__(self):
        """
        close the database
        :return:
        """
        self.conn.close()

    def get_list_maxnum_index(self, num_list, top):
        """
        get the index of the maximum number in the list
        :param num_list:
        :param top:
        :return:
        """
        num_dict = {}
        for i in range(len(num_list)):
            num_dict[i] = num_list[i]
        res_list = sorted(num_dict.items(), key=lambda e: e[1])
        max_num_index = [one[0] for one in res_list[::-1][:top]]

        return list(max_num_index)

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

    def construct_data_vocab(self):
        """
        construct vocabulary with only title
        :return:
        """
        for recipe in self.data_list:
            name = recipe['name']
            # ingredients = recipe['ingredients']

            term_tf = self.data_cleanup_tf(name)[1]

            for term in term_tf.keys():
                self.vocab.add(term)

            self.cleaned_data_list.append(list(term_tf.keys()))

    def write_row_to_db(self, rid_self, rid_list):
        """
        write each row into database
        :param rid_cur:
        :param rid_list:
        :return:
        """
        c = self.conn.cursor()

        values = (rid_self, rid_list[0], rid_list[1], rid_list[2], rid_list[3], rid_list[4])
        c.execute('insert into k_nearest values (?, ?, ?, ?, ?, ?)', values)

        self.conn.commit()

    def construct_k_nearest(self):
        """
        construct the k nearest rid
        :return:
        """
        word2id = {}
        for word_id, word in enumerate(self.vocab):
            word2id[word] = word_id

        row2rid = {}  # convert the row id to the recipe id

        matrix_size = (self.data_n, len(word2id))
        X = dok_matrix(matrix_size)

        for i, recipe in enumerate(self.data_list):
            rid = recipe['id']
            name = recipe['name']

            row2rid[i] = rid

            term_tf = self.data_cleanup_tf(name)[1]
            for term, tf in term_tf.items():
                X[i, word2id[term]] = tf

        knn = NearestNeighbors(n_neighbors=6).fit(X)
        for row, x in enumerate(self.cleaned_data_list):
            x_in = dok_matrix((1, len(word2id)))
            for term in x:
                x_in[0, word2id[term]] += 1
                # print(word2id[term])
                # print(x_in)

            neighbours = knn.kneighbors(x_in, 6, return_distance=False)[0]
            rid_self = row2rid[row]
            rid_list = list(set([row2rid[row] for row in neighbours]) - set([rid_self]))
            # print(neighbours)
            # print([row2rid[row] for row in neighbours])
            # print(rid_self)
            # print(rid_list)
            self.write_row_to_db(rid_self, rid_list)

        # dictionary = corpora.Dictionary(cleaned_data_list)  # generate the dictionary
        # corpus = [dictionary.doc2bow(item) for item in cleaned_data_list]
        # tfidf = models.TfidfModel(corpus)
        # num_features = len(dictionary.token2id.keys())  # number of terms in the dictionary
        # index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=num_features)

        # for i, data in enumerate(cleaned_data_list):
        #     vector = dictionary.doc2bow(data)  # convert to svm
        #     sims = index[tfidf[vector]]
        #     row_list = self.get_list_maxnum_index(list(sims), 6)
        #     rid_list = [row2rid[row] for row in row_list]
        #     self.write_row_to_db(row2rid[i], rid_list.remove(row2rid[i])[:5])

    def find_k_nearest(self):
        """
        find the k nearest rid and write to database
        :return:
        """
        self.construct_data_vocab()
        self.construct_k_nearest()


if __name__ == '__main__':
    print('-----start time: %s-----' % (datetime.today()))
    rm = RecommendationModule()
    rm.find_k_nearest()
    print('-----finish time: %s-----' % (datetime.today()))
