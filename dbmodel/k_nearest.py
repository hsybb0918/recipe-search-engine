# @File        : k_nearest.py
# @Description :
# @Time        : 07 March, 2021
# @Author      : Cyan
from sqlalchemy import Table
from controller.utils import dbconnect

dbsession, md, dbbase = dbconnect()


class K_nearest(dbbase):
    __table__ = Table('k_nearest', md, autoload=True)

    def find_knn(self, rid):
        """
        return the five nearest recipes by rid
        :param rid:
        :return:
        """
        row = dbsession.query(K_nearest.nn1, K_nearest.nn2, K_nearest.nn3, K_nearest.nn4, K_nearest.nn5)\
            .filter_by(id=rid).first()
        return [row[0], row[1], row[2], row[3], row[4]]
