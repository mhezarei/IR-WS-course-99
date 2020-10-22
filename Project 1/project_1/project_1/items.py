# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Project1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Event(scrapy.Item):
    title = scrapy.Field()
    holding_time = scrapy.Field()
    holding_status = scrapy.Field()
    holder = scrapy.Field()
    prices = scrapy.Field()
    registration_dates = scrapy.Field()
    description_path = scrapy.Field()
