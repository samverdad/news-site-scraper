from urllib.parse import urlencode
from dotenv import load_dotenv
import scrapy
import os

load_dotenv()
API_KEY = os.environ.get("API_KEY")

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    # proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class NewsSiteScraperSpider3(scrapy.Spider):
    name = 'newssitescraperspider3'

    def start_requests(self):
        start_url = 'https://www.malaysianow.com/search?query=ramadan+bazaar'
        yield scrapy.Request(url=get_proxy_url(start_url), callback=self.parse)

    def parse(self, response):
        selector = 'div.group.flex.flex-col.overflow-hidden.rounded-md.border-2.border-gray-100 a::attr(href)'
        for item_url in response.css(selector).getall():
            yield scrapy.Request(url=get_proxy_url(item_url), callback=self.scrape)

        # next_page_url = response.css('').get()
        
        # if next_page_url:
        #     yield scrapy.Request(get_proxy_url(next_page_url), callback=self.parse)

    def crawl(self, response):
        yield response

    def scrape(self, response):
        yield {
            'title': response.css('h1.font-georgia.text-4xl::text').get(),
            'author': response.css('span.font-source-sans.font-semibold.text-gray-700 a::text').get(),
            'location': '',
            'datetime': response.css('span.pr-3.font-source-sans.text-gray-700').xpath('./time/@datetime').get(),
            'content': response.css('div#content-wrap p::text').getall(),
        }
