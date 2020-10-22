# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.exporters import JsonItemExporter


class Project1Pipeline:
    def process_item(self, item, spider):
        return item


class JsonPipeline(object):
    def __init__(self, name):
        self.file = open(name + ".json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False, indent=4)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        """
        After the spider is done crawling, we need to save the json file in
        the corresponding mongoDB collection which is the `events` database.
        
        The name of the json files and the collections are the timestamp of
        when the crawling was done.
        
        The timestamp is given as a command-line argument from the program
        that runs the crawler periodically.
        
        :param spider: The events spider.
        """
        self.exporter.finish_exporting()
        self.file.close()
        
        client = MongoClient("localhost:27017")
        db = client["events"]
        events = db[self.file.name.split('.')[0]]
        with open(self.file.name) as file:
            data = json.load(file)
        events.delete_many({})
        events.insert_many(data)
        client.close()
        print("Done!")

    @classmethod
    def from_crawler(cls, crawler):
        name = getattr(crawler.spider, 'name')
        return cls(name)
