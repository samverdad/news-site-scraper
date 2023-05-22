from urllib.parse import urlencode
from dotenv import load_dotenv
import scrapy
import os

load_dotenv()
API_KEY = os.environ.get("API_KEY")

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

class NewsSiteScraperSpider2(scrapy.Spider):
    name = 'newssitescraperspider2'

    def start_requests(self):
        start_url = 'https://www.malaymail.com/search?query=ramadan+bazaar'
        yield scrapy.Request(url=get_proxy_url(start_url), callback=self.parse)

    def parse(self, response):
        selector = 'h2.article-title a::attr(href)'
        for item_url in response.css(selector).getall():
            yield scrapy.Request(url=get_proxy_url(item_url), callback=self.scrape, cb_kwargs={'url': item_url})

        next_page_url = response.css('li.pager-nav a::attr(href)').get()
        
        if next_page_url:
            yield scrapy.Request(get_proxy_url(next_page_url), callback=self.parse)

    def crawl(self, response):
        yield response

    def scrape(self, response, url):
        yield {
            'title': response.css('h1.article-title::text').get(),
            'author': response.css('div.article-byline::text').getall(), # to improve by removing 'By' and trailing spaces
            'location': '',
            'datetime': response.css('div.article-date::text').get(),
            'content': response.css('div.article-body p::text').getall(),
            'url': url,
        }
