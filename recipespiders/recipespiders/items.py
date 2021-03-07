# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class RecipespidersItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()  # recipe id
    name = scrapy.Field()  # recipe name -> regular search
    description = scrapy.Field()  # description -> regular search

    rating_num = scrapy.Field()  # number of rating -> rating sort (popular)
    rating_star = scrapy.Field()  # rating mapping -> rating sort
    rating_score = scrapy.Field()  # rating score -> rating sort

    total_time = scrapy.Field()  # recipe total time -> time filter
    ingredients = scrapy.Field()  # ingredients
    steps = scrapy.Field()  # steps

    photo_url = scrapy.Field()  # url of photo
    record_url = scrapy.Field()  # url of detail
