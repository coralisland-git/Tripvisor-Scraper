# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv

import time

import datetime

from scrapy import signals

from scrapy.contrib.exporter import CsvItemExporter


class ChainxyPipeline(object):

    def __init__(self):

        self.files = {}


    @classmethod
    def from_crawler(cls, crawler):

       pass


    def spider_opened(self, spider):

        pass    


    def spider_closed(self, spider):
        
        pass