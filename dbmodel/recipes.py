# @File        : recipes.py
# @Description :
# @Time        : 07 March, 2021
# @Author      : Cyan
import random

from sqlalchemy import Table
from controller.utils import dbconnect

dbsession, md, dbbase = dbconnect()


class Recipes(dbbase):
    __table__ = Table('recipes', md, autoload=True)

    def find_by_id(self, rid):
        """

        :param rid:
        :return:
        """
        row = dbsession.query(Recipes).filter_by(id=rid).first()
        return row

    def find_by_ids(self, rids):
        """

        :param rids:
        :return:
        """
        rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids)).order_by(Recipes.rating_num.desc()).limit(5)
        return rows

    def find_by_ids_limited(self, rids, left, right):
        """

        :param ids:
        :return:
        """
        if left != None and right == None:
            # left limit
            rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids), Recipes.total_time >= left)\
                .order_by(Recipes.rating_num.desc()).limit(5)
        elif left == None and right != None:
            # right limit
            rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids), Recipes.total_time <= right) \
                .order_by(Recipes.rating_num.desc()).limit(5)
        else:
            # both limit
            rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids), Recipes.total_time >= left, Recipes.total_time <= right)\
                .order_by(Recipes.rating_num.desc()).limit(5)
        return rows


    def find_rand_recipes(self, num):
        """

        :param num:
        :return:
        """
        count = dbsession.query(Recipes).count()
        rand = [random.randint(1, count) for _ in range(num)]
        rows = dbsession.query(Recipes).filter(Recipes.id.in_(rand)).all()
        return rows

    def find_by_name_fuzzy(self, r_name):
        """

        :param r_name:
        :return:
        """
        rows = dbsession.query(Recipes).filter(Recipes.name.like('%{keyword}%'.format(keyword=r_name))).limit(5)
        return rows

    def to_json(self):
        """

        :return:
        """
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict