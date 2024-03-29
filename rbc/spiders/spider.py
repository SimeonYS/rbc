import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import RbvItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class RbvSpider(scrapy.Spider):
	name = 'rbc'
	start_urls = ['http://www.rbc.com/newsroom/news/index.html']

	def parse(self, response):
		articles = response.xpath('//div[contains(@class,"contentframework-container-content content-")]//p')
		for article in articles:
			date = article.xpath('.//span[@class="newsDate"]/text()').get()
			post_links = article.xpath('.//span[@class="newsUrl"]/a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@id="layout-column-main"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=RbvItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
