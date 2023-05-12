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

class NewsSiteScraperSpider(scrapy.Spider):
    name = 'newssitescraperspider'

    def start_requests(self):
        start_url = 'https://www.freemalaysiatoday.com/?s=ramadan+bazaar&c=all'
        yield scrapy.Request(url=get_proxy_url(start_url), callback=self.parse)

    def parse(self, response):
        selector = 'article a.summary-title-link::attr(href)'
        for item_url in response.css(selector).getall():
            yield scrapy.Request(url=get_proxy_url('https://www.freemalaysiatoday.com' + item_url), callback=self.scrape)

        # next_page_url = response.css('').get()
        
        # if next_page_url:
        #     yield scrapy.Request(get_proxy_url(next_page_url), callback=self.parse)

    def crawl(self, response):
        yield response

    def scrape(self, response):
        yield {
            'title': response.css('h1.Page__PostTitleH1-sc-1auxjzz-0::text').get(),
            'author': response.css('span.author a.Style__StyledAnchor-sc-kwuyeg-0::text').get(),
            'location': '',
            'datetime': response.css('div').xpath('./time/@datetime').get(), # to fix
            'content': response.css('div.Content__StyledDiv-sc-1n9vywj-0 p::text').getall(),
        }
