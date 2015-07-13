import scrapy
import pprint
import sys

class StackOverflowSpider(scrapy.Spider):
	name = 'evodraft'
	start_urls = ['http://stackoverflow.com/questions?sort=votes']

	def parse(self, response):
		full_url = "http://evo2015.s3.amazonaws.com/brackets/ssbm_a101.html"
		yield scrapy.Request(full_url, callback=self.parse_question)

	def parse_question(self, response):
		yield {'w-handles': response.css('.winners .players .player-handle::text').extract(),
			'l-handles': response.css('.losers .players .player-handle::text').extract()}
