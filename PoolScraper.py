import scrapy
import pprint
import sys

class StackOverflowSpider(scrapy.Spider):
	name = 'evodraft'
	start_urls = ['http://stackoverflow.com/questions?sort=votes']

	def parse(self, response):
		full_url = "http://jordanverasamy.github.io/evo/ExampleBracket.html"
		yield scrapy.Request(full_url, callback=self.parse_question)

	def parse_question(self, response):
		yield {'winners-r1': response.css('.winners .match-1x .players .player-handle::text').extract(),
			'winners-r2': response.css('.winners .match-2x .players .player-handle::text').extract(),
			'winners-r3': response.css('.winners .match-4x .players .player-handle::text').extract(),
			'winners-r4': response.css('.winners .match-8x .players .player-handle::text').extract(),
			'winners-qual': response.css('.column-qualify .match-8x .players .player-handle::text').extract(),
			'losers-r1': response.css('.losers1 .match-1x .players .player-handle::text').extract(),
			'losers-r2': response.css('.losers2 .match-1x .players .player-handle::text').extract(),
			'losers-r3': response.css('.losers1 .match-2x .players .player-handle::text').extract(),
			'losers-r4': response.css('.losers2 .match-2x .players .player-handle::text').extract(),
			'losers-r5': response.css('.losers1 .match-4x .players .player-handle::text').extract(),
			'losers-r6': response.css('.losers2 .match-4x .players .player-handle::text').extract(),
			'losers-qual': response.css('.column-qualify .match-4x .players .player-handle::text').extract()}
