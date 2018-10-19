import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from selenium import webdriver

from scrapy.xlib.pydispatch import dispatcher

from scrapy import signals

from lxml import etree

from lxml import html

from chainxy.items import ChainItem

from scrapy.contrib.exporter import CsvItemExporter

import time

import pdb


class tripadvisor(scrapy.Spider):

	name = 'tripadvisor'

	domain = 'https://www.tripadvisor.com'

	history = []

	credentials = []

	result = []

	ordered = []

	count = 0


	def __init__(self):

		dispatcher.connect(self.spider_closed, signals.spider_closed)

		chrome_options = webdriver.ChromeOptions()

		chrome_options.add_argument("headless")

		self.driver = webdriver.Chrome(chrome_options=chrome_options)


	def start_requests(self):

		url = 'https://www.tripadvisor.com/'

		yield scrapy.Request(url, callback=self.parse)


	def parse(self, response):

		hotel_list = []

		self.driver.get('https://www.tripadvisor.com/')

		location = raw_input(' Location : ')

		self.driver.find_element_by_class_name('typeahead_input').send_keys(location)

		self.driver.find_element_by_class_name('form_submit').click()

		time.sleep(3)

		self.driver.find_element_by_id("global-nav-attractions").click()

		time.sleep(3)

		source = self.driver.page_source.encode("utf8")

		tree = etree.HTML(source)

		post_list = tree.xpath('//div[@class="attraction_clarity_cell"]')

		for post in post_list:

			name = self.validate(post.xpath('.//div[contains(@class, "listing_title")]/a//text()')[0])

			if '(' not in name:

				if len(hotel_list) > 50:

					break

				hotel_list.append(post)

		pagenation = tree.xpath('//div[contains(@class, "pageNumbers")]//a/@href')
 
		if pagenation and len(hotel_list) < 50:

			for page in pagenation:

				self.driver.get(self.domain + page)

				time.sleep(2)

				source = self.driver.page_source.encode("utf8")

				tree = etree.HTML(source)

				post_list = tree.xpath('//div[@class="attraction_clarity_cell"]')

				if len(hotel_list) < 50 : 

					for post in post_list:

						name = self.validate(post.xpath('.//div[contains(@class, "listing_title")]/a//text()')[0])

						if '(' not in name:

							if len(hotel_list) > 50:

								break

							hotel_list.append(post)

		for hotel in hotel_list :

			try:

				item = ChainItem()

				item['name'] = self.validate(hotel.xpath('.//div[contains(@class, "listing_title")]/a//text()')[0])

				self.ordered.append(item)

				try:

					item['link'] = self.domain + self.validate(hotel.xpath('.//a[contains(@class, "photo_link")]/@href')[0])

				except:

					item['link'] = self.domain + self.validate(hotel.xpath('.//a[contains(@class, "photo_link")]/@onclick')[0]).split("Attractions_List_Click', '")[1].split("',")[0].strip()

				try:

					item['image'] = self.validate(hotel.xpath('.//img[@class="photo_image"]/@src')[0])

				except:

					pass

				yield scrapy.Request(url = item['link'], callback=self.parse_detail, meta={'item': item})

			except Exception as e:
				
				pass


	def parse_detail(self, response):

		try:

			item = response.meta['item']

			item['address'] = ' '.join(response.xpath('//div[contains(@class, "is-hidden-mobile blEntry address ui_link")]//span[@class="detail"]//text()').extract())

			self.result.append(item)

		except:

			pass


	def spider_closed(self, spider):
		
		try:

			file = open('res.csv', 'w+b')

			self.exporter = CsvItemExporter(file)

			self.exporter.fields_to_export = ['name', 'image', 'link', 'address']

			self.exporter.start_exporting()

			for item in self.ordered:

				for res in self.result:

					if item['name'] == res['name']:

						self.exporter.export_item(item)

			self.exporter.finish_exporting()

			file.close()

		except:

			pass

	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').encode('raw-unicode-escape').replace('\xa0', ' ').strip()

		except:

			pass
