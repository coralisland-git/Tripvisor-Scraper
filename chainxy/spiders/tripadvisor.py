import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from selenium import webdriver

from lxml import etree

from lxml import html

from scrapy.xlib.pydispatch import dispatcher

from scrapy import signals

import time

import pdb


class tripadvisor(scrapy.Spider):

	name = 'tripadvisor'

	domain = ''

	history = []

	credentials = []

	result = []

	def __init__(self):

		filename = './result.json'

		os.remove(filename) if os.path.exists(filename) else None

		dispatcher.connect(self.spider_closed, signals.spider_closed)

		self.driver = webdriver.Chrome("./chromedriver.exe")


	def start_requests(self):

		url = 'https://www.tripadvisor.com/'

		yield scrapy.Request(url, callback=self.parse)


	def parse(self, response):

		self.driver.get('https://www.tripadvisor.com/')

		location = raw_input(' Location : ')

		self.driver.find_element_by_class_name('typeahead_input').send_keys(location)

		self.driver.find_element_by_class_name('form_submit').click()

		time.sleep(2)

		self.driver.find_element_by_id("global-nav-attractions").click()	

		time.sleep(3)	

		source = self.driver.page_source.encode("utf8")

		tree = etree.HTML(source)

		post_list = tree.xpath('//div[@class="attraction_clarity_cell"]')

		time.sleep(2)

		for post in post_list :

			try:


				item = {

					'name' : self.validate(post.xpath('.//div[contains(@class, "listing_title")]/a//text()')[0]),

					'image' : self.validate(post.xpath('.//img[@class="photo_image"]/@src')[0]),

					'link' : 'https://www.tripadvisor.com'+self.validate(post.xpath('.//a[@class="photo_link "]/@href')[0]),

					'lat' : '',

					'lng' : ''

				}

				yield scrapy.Request(url = item['link'], callback=self.parse_detail, meta={'item': item})

			except:

				pass


	def parse_detail(self, response):

		try:

			data = response.body.split('&center=')[1].split('&maptype=roadmap')[0]

			item = response.meta['item']

			item['lat'] = data.split(',')[0]

			item['lng'] = data.split(',')[1]

			self.result.append(item)

		except:

			pass


	def spider_closed(self, spider):
		
		try:

			with open('result.json', 'w') as outfile:

				json.dump(self.result, outfile)

		except:

			pass

	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').encode('raw-unicode-escape').replace('\xa0', ' ').strip()

		except:

			pass



# with open('test.txt', 'wb') as f:
# 	f.write(response.body)