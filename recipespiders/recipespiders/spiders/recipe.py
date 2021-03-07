import json
import scrapy
from recipespiders.items import RecipespidersItem


class RecipeSpider(scrapy.Spider):
    name = 'recipe'

    start_urls = ['https://api.food.com/external/v1/nlp/search?pn=16800']
    base_url = 'https://api.food.com/external/v1/nlp/search?pn=%d'
    page_num = 16801

    recipe_count = 166121

    def parse_detail(self, response):
        """
        parse the detail page
        :param response:
        :return:
        """
        # get item
        item = response.meta['item']

        # process ingredients
        ing_list = []
        ing_li = response.xpath('//*[@id="__layout"]//ul[@class="recipe-ingredients__list"]/li')
        for li in ing_li:
            ing = li.xpath('.//a/text()').extract_first()
            if ing is not None:
                ing_list.append(ing.strip())
        item['ingredients'] = ', '.join(ing_list)

        # process steps
        step_list = []
        step_li = response.xpath('//*[@id="__layout"]//li[@class="recipe-directions__step"]')
        for li in step_li:
            step = li.xpath('.//text()').extract_first()
            if step is not None:
                step_list.append(step.strip())
        item['steps'] = '\n'.join(step_list)

        yield item

    def parse(self, response):
        """
        parse the search page
        :param response:
        :return:
        """
        recipes = json.loads(response.text)['response']['results']
        # test json data
        # fp = open("./food.json", "w", encoding="utf-8")
        # json.dump(recipes, fp=fp, ensure_ascii=False)
        for recipe in recipes:
            if recipe['record_type'] == 'Recipe':
                item = RecipespidersItem()

                self.recipe_count += 1
                item['id'] = self.recipe_count
                item['name'] = recipe['main_title']
                item['description'] = recipe['main_description']

                item['rating_num'] = int(recipe['main_num_ratings'])
                item['rating_star'] = int(recipe['main_rating_mapping'])
                item['rating_score'] = float(recipe['main_rating'])

                item['total_time'] = int(recipe['recipe_totaltime'])

                if recipe.get('recipe_photo_url') is None:
                    continue
                else:
                    item['photo_url'] = recipe['recipe_photo_url']

                item['record_url'] = recipe['record_url']

                yield scrapy.Request(url=recipe['record_url'], callback=self.parse_detail, meta={'item': item})

        # process remaining pages
        if self.page_num <= 21000:
            print(self.page_num)
            new_url = format(self.base_url % self.page_num)
            self.page_num += 1

            yield scrapy.Request(url=new_url, callback=self.parse)
