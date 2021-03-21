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

    def get_sort_list(self, rids, stype):
        """
        according to sort type, return the sorted recipes
        :param rids:
        :param stype:
        :return:
        """
        if stype == 0:  # most relevant
            return dbsession.query(Recipes).filter(Recipes.id.in_(rids))
        elif stype == 1:  # highest score
            return dbsession.query(Recipes).filter(Recipes.id.in_(rids)).order_by(Recipes.rating_score.desc())
        elif stype == 2:  # lowest score
            return dbsession.query(Recipes).filter(Recipes.id.in_(rids)).order_by(Recipes.rating_score)
        elif stype == 3:  # highest comments
            return dbsession.query(Recipes).filter(Recipes.id.in_(rids)).order_by(Recipes.rating_num.desc())
        elif stype == 4:  # lowest comments
            return dbsession.query(Recipes).filter(Recipes.id.in_(rids)).order_by(Recipes.rating_num)

    def find_by_id(self, rid):
        """
        according to recipe id, return the recipe
        :param rid:
        :return:
        """
        row = dbsession.query(Recipes).filter_by(id=rid).first()
        return row

    def find_by_ids(self, rids):
        """
        according to id list, return recipes in the list
        :param rids:
        :return:
        """
        rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids))
        return rows

    def find_by_ids_limited(self, rids, left, right):
        """
        according to time filtering, return the required recipes
        :param ids:
        :return:
        """
        if left != None and right == None:
            # left limit
            rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids), Recipes.total_time >= left)
        elif left == None and right != None:
            # right limit
            rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids), Recipes.total_time <= right)
        else:
            # both limit
            rows = dbsession.query(Recipes).filter(Recipes.id.in_(rids), Recipes.total_time >= left,
                                                   Recipes.total_time <= right)
        return rows

    def find_rand_recipes(self, num):
        """
        every time return a number of random recipes
        :param num:
        :return:
        """
        count = dbsession.query(Recipes).count()
        rand = [random.randint(1, count) for _ in range(num)]
        rows = dbsession.query(Recipes).filter(Recipes.id.in_(rand)).all()
        return rows

    def find_by_name_fuzzy(self, r_name):
        """
        return recipes by fuzzy search
        :param r_name:
        :return:
        """
        rows = dbsession.query(Recipes).filter(Recipes.name.like('%{keyword}%'.format(keyword=r_name))).limit(5)
        return rows

    def to_json(self):
        """
        change the recipe to json data
        :return:
        """
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
