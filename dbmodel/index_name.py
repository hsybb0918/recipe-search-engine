# @File        : index_name.py
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


class Index_name(dbbase):
    __table__ = Table('index_name', md, autoload=True)

    stop_words = get_stopwords()
    stemmer = Porter2Stemmer()

    DATA_N = 163249
    AVG_LEN = 33.782259003117936

    def fetch_from_db(self, term):
        """
        fetch the corresponding index from database
        :param term:
        :param table_name:
        :return:
        """
        row = dbsession.query(Index_name).filter_by(term=term).first()
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

    def result_by_tfidf(self, query):
        """
        query by tfidf, for only title
        :param query:
        :return:
        """
        n, tf_dict = self.data_cleanup_tf(query)

        tfidf_scores = {}
        for term in tf_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r.df
            idf = math.log(self.DATA_N / df)

            posting_list = r.postings.split('\n')
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
