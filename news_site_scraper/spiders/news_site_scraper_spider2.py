from urllib.parse import urlencode
from dotenv import load_dotenv
import scrapy
import os

load_dotenv()
PROXY_URL = os.environ["PROXY_URL"]
API_KEY = os.environ["API_KEY"]

DOMAIN_NAME = 'https://www.malaymail.com'

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = PROXY_URL + '?' + urlencode(payload)
    return proxy_url

class NewsSiteScraperSpider2(scrapy.Spider):
    name = 'newssitescraperspider2'

    def start_requests(self):
        start_url = DOMAIN_NAME + '/search?query=ramadan+bazaar'
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
        # remove 'By' and trailing spaces from `author`
        author_data = response.css('div.article-byline::text').getall()
        author = [s.strip().replace('By', '') for s in author_data]
        author = ', '.join(author)

        yield {
            'title': response.css('h1.article-title::text').get(),
            'author': author,
            'location': '',
            'datetime': response.css('div.article-date::text').get(),
            'content': response.css('div.article-body p::text').getall(),
            'url': url,
        }
