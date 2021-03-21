# @File        : index_name_desc_ing.py
# @Description :
# @Time        : 07 March, 2021
# @Author      : Cyan
import math
import operator
import re

from porter2stemmer import Porter2Stemmer
from sqlalchemy import Table
from controller.utils import dbconnect, get_stopwords

dbsession, md, dbbase = dbconnect()


class Index_name_desc_ing(dbbase):
    __table__ = Table('index_name_desc_ing', md, autoload=True)

    stop_words = get_stopwords()
    stemmer = Porter2Stemmer()

    DATA_N = 163249
    AVG_LEN = 33.782259003117936
    K1 = 1.5
    B = 0.75

    def fetch_from_db(self, term):
        """
        fetch the corresponding index from database
        :param term:
        :param table_name:
        :return:
        """
        row = dbsession.query(Index_name_desc_ing).filter_by(term=term).first()
        return row

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

    def result_by_bm25(self, query):
        """
        query by bm25, for all text
        :param query:
        :return:
        """
        n, tf_dict = self.data_cleanup_tf(query)

        bm25_scores = {}
        for term in tf_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r.df
            idf = math.log((self.DATA_N - df + 0.5) / (df + 0.5))

            posting_list = r.postings.split('\n')
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
        return result
