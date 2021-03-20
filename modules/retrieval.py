# @File        : retrieval.py
# @Description :
# @Time        : 04 March, 2021
# @Author      : Cyan
import configparser
import math
import operator
import re
import sqlite3
from datetime import datetime
from porter2stemmer import Porter2Stemmer


class RetrievalModule:
    stop_words = set()  # set of stop words
    stemmer = Porter2Stemmer()  # init porter stemmer

    config_path = None
    config = None

    conn = None

    DATA_N = 0
    AVG_LEN = 0
    K1 = 0
    B = 0

    def __init__(self):
        """
        init the variables
        """
        self.config_path = 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path, 'utf-8')

        with open(self.config['DEFAULT']['STOPWORDS_PATH'], encoding='utf-8') as f:
            self.stop_words = set(f.read().split())

        self.conn = sqlite3.connect(self.config['DEFAULT']['SE_DB_PATH'])
        self.DATA_N = int(self.config['DEFAULT']['DATA_N'])
        self.AVG_LEN = float(self.config['DEFAULT']['AVG_LEN'])
        self.K1 = float(self.config['DEFAULT']['PARAM_K1'])
        self.B = float(self.config['DEFAULT']['PARAM_B'])

    def __del__(self):
        """
        close the database
        :return:
        """
        self.conn.close()

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

    def fetch_from_db(self, term, table_name):
        """
        fetch the corresponding index from database
        :param term:
        :param table_name:
        :return:
        """
        c = self.conn.cursor()
        c.execute('select * from %s where term=?' % table_name, (term,))
        return c.fetchone()

    def result_by_bm25(self, query):
        """
        query by bm25, for title, description and ingredients
        :param query:
        :return:
        """
        n, tf_dict = self.data_cleanup_tf(query)

        bm25_scores = {}
        for term in tf_dict.keys():
            r = self.fetch_from_db(term, 'index_name_desc_ing')
            if r is None:
                continue
            df = r[1]
            idf = math.log((self.DATA_N - df + 0.5) / (df + 0.5))

            posting_list = r[2].split('\n')
            for posting in posting_list:
                rid, tf, length = posting.split('\t')
                rid = int(rid)
                tf = int(tf)
                length = int(length)
                s = ((self.K1 + 1) * tf * idf) / (tf + self.K1 * (1 - self.B + self.B * length / self.AVG_LEN))
                if rid in bm25_scores:
                    bm25_scores[rid] = bm25_scores[rid] + s
                else:
                    bm25_scores[rid] = s

        bm25_scores = sorted(bm25_scores.items(), key=operator.itemgetter(1))
        bm25_scores.reverse()

        result = [x[0] for x in bm25_scores]
        # print(len(bm25_scores), len(result))
        if len(result) == 0:
            return 0, []
        else:
            return 1, result

    def result_by_tfidf(self, query):
        """
        query by tfidf, for only title
        :param query:
        :return:
        """
        n, tf_dict = self.data_cleanup_tf(query)

        tfidf_scores = {}
        for term in tf_dict.keys():
            r = self.fetch_from_db(term, 'index_name')
            if r is None:
                continue
            df = r[1]
            idf = math.log(self.DATA_N / df)

            posting_list = r[2].split('\n')
            for posting in posting_list:
                rid, tf, length = posting.split('\t')
                rid = int(rid)
                tf = int(tf)
                s = (1 + math.log(tf)) * idf * tf_dict[term]
                if rid in tfidf_scores:
                    tfidf_scores[rid] = tfidf_scores[rid] + s
                else:
                    tfidf_scores[rid] = s

        tfidf_scores = sorted(tfidf_scores.items(), key=operator.itemgetter(1))
        tfidf_scores.reverse()

        result = [x[0] for x in tfidf_scores]
        # print(len(tfidf_scores), len(result))
        if len(result) == 0:
            return 0, []
        else:
            return 1, result

    def search(self, query, sort_type):
        """
        combine two kinds of search
        :param query:
        :param sort_type:
        :return:
        """
        if sort_type == 0:  # search for all text
            return self.result_by_bm25(query)
        elif sort_type == 1:  # search for title
            return self.result_by_tfidf(query)


if __name__ == "__main__":
    print('-----start time: %s-----' % (datetime.today()))
    rm = RetrievalModule()
    flag, rs = rm.search('meatloaf garlic', 1)
    print(rs)
    print('-----finish time: %s-----' % (datetime.today()))
