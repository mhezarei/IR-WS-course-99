import scrapy
import re
from ..items import Event


class EventsSpider(scrapy.Spider):
    name = "events"
    allowed_domains = ['evand.com']

    def start_requests(self):
        urls = ["https://evand.com/categories/%D8%AA%DA%A9%D9%86%D9%88%D9%84%D9%88%DA%98%DB%8C/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        event_xpath = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/div/section[@*]/div/div/a'
        # there are two possible xpath for next page ( first page and other pages )
        next_url_xpath1 = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/nav/ul/li/a'
        text_next_page = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/nav/ul/li/a/span'
        next_url_xpath2 = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/nav/ul/li[2]/a'

        # get all events link in a page at first
        events = response.xpath(event_xpath)
        yield from response.follow_all(events, self.parse_event)

        # if next page exist it should be crawled as new link
        next_page_url1 = response.xpath(next_url_xpath1)
        next_page_url2 = response.xpath(next_url_xpath2)

        if next_page_url1 is not None and 'صفحه بعد' in response.xpath(text_next_page).get():
            yield response.follow(url=next_page_url1[0], callback=self.parse)
        elif next_page_url2 is not None:
            yield response.follow(url=next_page_url2[0], callback=self.parse)

    # a function with extracting html header text functionality
    @staticmethod
    def extract_header(html_code: str) -> str:
        html_header = re.search(r'<h[1-6] [a-zA-Z0-9-\"= ]*>(.+?)</h[1-6]>', html_code).group(1)
        return html_header

    # a function with extracting html span texts functionality
    @staticmethod
    def extract_span_text(html_code: str) -> str:
        html_span_text = re.search(r'<span [a-zA-Z0-9-\"= ]*>(.+?)</span>', html_code).group(1)
        return html_span_text

    # a function due to indicating an event is online or in-person
    def indicate_holding_status(self, html_code: str) -> str:
        html_span_text = self.extract_span_text(html_code=html_code)
        return 'Online' if html_span_text == 'آنلاین' else 'In-Person'

    def parse_event(self, response):
        # define our desired XPaths to use it later
        event_title_xpath = '//*[@id="page"]/div/header/section/div[2]/div[1]/h1'
        holding_time_xpath = '//*[@id="page"]/div/header/section/div[2]/div[1]/div/span'
        holding_status_xpath = '//*[@id="page"]/div/header/section/div[2]/div[2]/ul/li[2]/div/span'
        holder_xpath = '//*[@id="page"]/div/div[2]/div/div[1]/div/div/div/div[@*]/div/section/a/div/h4'

        event_title = self.extract_header(html_code=response.xpath(event_title_xpath).get())
        holding_time = self.extract_span_text(response.xpath(holding_time_xpath).get())
        holding_status = self.indicate_holding_status(response.xpath(holding_status_xpath).get())
        holder = self.extract_header(html_code=response.xpath(holder_xpath).get())

        item = Event()
        item['event_title'] = event_title
        item['holding_time'] = holding_time
        item['holding_status'] = holding_status
        item['holder'] = holder

        yield item
