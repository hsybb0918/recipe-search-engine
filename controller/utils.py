# @File        : utils.py
# @Description :
# @Time        : 07 March, 2021
# @Author      : Cyan
import os
from sqlalchemy import MetaData


def dbconnect():
    """
    get the database connection
    :return:
    """
    from app import db
    dbsession = db.session
    md = MetaData(bind=db.engine)
    dbbase = db.Model

    return (dbsession, md, dbbase)


def get_stopwords():
    """

    :return:
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    data_file = os.path.join(basedir, '../data/englishST.txt')

    with open(data_file, encoding='utf-8') as f:
        stop_words = set(f.read().split())

    return stop_words
