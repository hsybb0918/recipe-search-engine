# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from scrapy.utils.project import get_project_settings


class RecipespidersPipeline:
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
