import scrapy


class Event(scrapy.Item):
    event_title = scrapy.Field()
    holding_time = scrapy.Field()
    holding_status = scrapy.Field()
    holder = scrapy.Field()
