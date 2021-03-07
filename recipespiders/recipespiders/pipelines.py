# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import sqlite3
import pymongo
from scrapy.utils.project import get_project_settings


class RecipeMongoDBPipeline:
    sheet = None

    def __init__(self):
        """
        init the database connection
        """
        # get the settings of database
        settings = get_project_settings()
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbname = settings['MONGODB_DBNAME']
        sheetname = settings['MONGODB_SHEETNAME']

        # create the connection
        client = pymongo.MongoClient(host=host, port=port)

        # specify the sheet
        self.sheet = client[dbname][sheetname]

    def process_item(self, item, spider):
        """
        store to database
        :param item:
        :param spider:
        :return:
        """
        # insert into database
        self.sheet.insert(dict(item))

        return item


class RecipeSQLitePipeline:
    conn = None
    c = None

    def __init__(self):
        """
        init database
        """
        self.conn = sqlite3.connect('se_former.db')
        # self.c = self.conn.cursor()

        # self.c.execute('drop table if exists recipes')
        # self.c.execute('create table recipes ('
        #                'id integer primary key, name text, description text, '
        #                'rating_num integer, rating_star integer, rating_score real, '
        #                'total_time integer, ingredients text, steps text, '
        #                'photo_url text, record_url text)')

    def __del__(self):
        """
        disconnect after crawling
        :return:
        """
        self.conn.close()

    def process_item(self, item, spider):
        """
        commit to database
        :param item:
        :param spider:
        :return:
        """
        self.c = self.conn.cursor()
        values = (item['id'], item['name'], item['description'],
                  item['rating_num'], item['rating_star'], item['rating_score'],
                  item['total_time'], item['ingredients'], item['steps'],
                  item['photo_url'], item['record_url'])

        self.c.execute('insert into recipes values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
        self.conn.commit()

        return item
