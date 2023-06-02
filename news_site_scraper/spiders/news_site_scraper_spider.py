from urllib.parse import urlencode
from dotenv import load_dotenv
import scrapy
import os

load_dotenv()
PROXY_URL = os.environ["PROXY_URL"]
API_KEY = os.environ["API_KEY"]

DOMAIN_NAME = 'https://www.freemalaysiatoday.com'

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = PROXY_URL + '?' + urlencode(payload)
    return proxy_url

class NewsSiteScraperSpider(scrapy.Spider):
    name = 'newssitescraperspider'

    def start_requests(self):
        start_url = DOMAIN_NAME + '/?s=ramadan+bazaar&c=all'
        yield scrapy.Request(url=get_proxy_url(start_url), callback=self.parse)

    def parse(self, response):
        selector = 'article a.summary-title-link::attr(href)'
        for item_url in response.css(selector).getall():
            yield scrapy.Request(url=get_proxy_url(DOMAIN_NAME + item_url), callback=self.scrape, cb_kwargs={'url': item_url})

        # next_page_url = response.css('').get()
        
        # if next_page_url:
        #     yield scrapy.Request(get_proxy_url(next_page_url), callback=self.parse)

    def crawl(self, response):
        yield response

    def scrape(self, response, url):
        yield {
            'title': response.css('h1.Page__PostTitleH1-sc-1auxjzz-0::text').get(),
            'author': response.css('span.author a.Style__StyledAnchor-sc-kwuyeg-0::text').get(),
            'location': '',
            'datetime': response.css('div').xpath('./time/@datetime').get(), # to fix
            'content': response.css('div.Content__StyledDiv-sc-1n9vywj-0 p::text').getall(),
            'url': DOMAIN_NAME + url,
        }
