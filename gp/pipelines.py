# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# from gp.connections import *
from gp.items import GPAppsItem, GPReviewItem
from scrapy.exporters import JsonLinesItemExporter
from pymongo import MongoClient
from scrapy.conf import settings
import logging

logger = logging.getLogger("pipeline")

def item_type(item):
    return type(item).__name__.replace('Item','').lower()

class GoogleplayspiderMongoDBPipeline(object):

    def __init__(self):
        self.logger = logging.getLogger("MongoDB")

    def open_spider(self, spider):
        self.connection = MongoClient(settings['MONGODB_URI'])
        self.db = self.connection[settings['MONGODB_DATABASE']]
        self.logger.info('Connection to MongoDB opened: DB %s', settings['MONGODB_DATABASE'])
    
    def close_spider(self, spider):
        self.connection.close()
        self.logger.info('Connection to MongoDB closed: DB %s', settings['MONGODB_DATABASE'])

    def process_item(self, item, spider):
        self.collection = self.db[item_type(item)]
        self.collection.insert(dict(item))
        return item

# class MongoPipeline(object):
#     def __init__(self):
#         connection = MongoClient(settings['MONGODB_HOST'], settings['MONGODB_PORT'])
#         self.db = connection[settings['MONGODB_DATABASE']]

#     def process_item(self, item, spider):
#         collection = self.db[type(item).__name__.lower()]
#         logging.info(collection.insert(dict(item)))
#         return item

class GoogleplayspiderJSONPipeline(object):

    saveTypes = ['gpapps', 'gpreview']

    def __init__(self):
        self.logger = logging.getLogger("JSONpipeline")
    
    def open_spider(self, spider):
        # self.files = dict([ (name, open(CSVDir+name+'.csv','w+b')) for name in self.SaveTypes ])
        # self.exporters = dict([ (name,CsvItemExporter(self.files[name])) for name in self.SaveTypes])
        
        # PC
        self.files = dict([ (name, open('D:/Local/MMA/' + name + '.json', 'wb')) for name in self.saveTypes]) 

        # MAC
        # self.files = dict([ (name, open(name + '.json', 'wb')) for name in self.saveTypes])
        
        self.exporters = dict([ (name, JsonLinesItemExporter(self.files[name], encoding='utf-8', ensure_ascii=False)) for name in self.saveTypes ])
        # self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        # self.exporter.start_exporting()
        [e.start_exporting() for e in self.exporters.values()]
        self.logger.info('JSON starts')
        
    def process_item(self, item, spider):
        what = item_type(item)
        if what in set(self.saveTypes):
            self.exporters[what].export_item(item)
        # self.exporter.export_item(item)
        return item
    
    def close_spider(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]
        self.logger.info('JSON ends')
        # self.exporter.finish_exporting()
        # self.file.close()

    # def __init__(self):
    #     # Storing output filename
    #     self.file_name = file_name
    #     # Creating a file handle and setting it to None
    #     self.file_handle = None

    # @classmethod
    # def from_crawler(cls, crawler):
    #     # getting the value of FILE_NAME field from settings.py
    #     output_file_name = crawler.settings.get('FILE_NAME')

    #     # cls() calls FanExportPipeline's constructor
    #     # Returning a FanExportPipeline object
    #     return cls(output_file_name)

    # def open_spider(self, spider):
    #     print('Custom export opened')

    #     # Opening file in binary-write mode
    #     file = open(self.file_name, 'wb')
    #     self.file_handle = file

    #     # Creating a FanItemExporter object and initiating export
    #     self.exporter = FanItemExporter(file)
    #     self.exporter.start_exporting()

    # def close_spider(self, spider):
    #     print('Custom Exporter closed')

    #     # Ending the export to file from FanItemExport object
    #     self.exporter.finish_exporting()

    #     # Closing the opened output file
    #     self.file_handle.close()

    # def process_item(self, item, spider):
    #     # passing the item to FanItemExporter object for expoting to file
    #     self.exporter.export_item(item)
    #     return item

