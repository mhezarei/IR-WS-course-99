import scrapy


class QuotesSpider(scrapy.Spider):
	name = "quotes"
	# instead of writing the start_requests method, create start_urls used by the default start_requests fucntion
	start_urls = [
		'http://quotes.toscrape.com/',
		# 'http://quotes.toscrape.com/page/1/',
		# 'http://quotes.toscrape.com/page/2/',
	]
	
	def parse(self, response, **kwargs):
		# getting the whole pages:
		# page = response.url.split("/")[-2]
		# filename = 'quotes-%s.html' % page
		# with open(filename, 'wb') as f:
		# 	f.write(response.body)
		# self.log('Saved file %s' % filename)
		
		# getting all the quotes from the page:
		# with open("/home/mh/Documents/Information Retrieval/HW1/tutorial/quotes.json", "r+") as f:
		# 	f.truncate(0)
		page_num = str(int(
			response.css('li.next a::attr(href)').get().split('/')[-2]) - 1)
		for quote in response.css('div.quote'):
			yield {
				'page_num': page_num,
				'author': quote.css('small.author::text').get(),
				'text': quote.css('span.text::text').get(),
				'tags': quote.css('div.tags a.tag::text').getall(),
			}
		
		# going to the next page using the link
		yield from response.follow_all(css='ul.pager a',
		                               callback=self.parse)  # automatically recognizes next
