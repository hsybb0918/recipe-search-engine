import scrapy


class RecipeSpider(scrapy.Spider):
    name = 'recipe'
    allowed_domains = ['www.food.com']
    start_urls = ['http://www.food.com/']

    def parse(self, response):
        pass
