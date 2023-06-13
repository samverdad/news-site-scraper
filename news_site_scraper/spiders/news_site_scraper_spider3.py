from urllib.parse import urlencode
from dotenv import load_dotenv
import scrapy
import os
import json


load_dotenv()
PROXY_URL = os.environ["PROXY_URL"]
API_KEY = os.environ["API_KEY"]

DOMAIN_NAME = 'https://www.malaysianow.com'
API_URL = 'https://api.malaysianow.com/graphql'

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = PROXY_URL + '?' + urlencode(payload)
    return proxy_url

class NewsSiteScraperSpider3(scrapy.Spider):
    name = 'newssitescraperspider3'

    def start_requests(self):
        config = self.req_config(curr_page=0)
        yield scrapy.FormRequest(url=get_proxy_url(config['api_url']), method="POST", headers=config['headers'], body=config['body'], callback=self.parse)

    def parse(self, response):
        self.crawl(response)

        total_pages = self.get_total_pages(response)

        if total_pages > 1:
            for page in range(1, total_pages):
                config = self.req_config(curr_page=page)
                yield scrapy.FormRequest(url=get_proxy_url(config['api_url']), method="POST", headers=config['headers'], body=config['body'], callback=self.crawl)

    def crawl(self, response):
        body = json.loads(response.body)
        articles = body['data']['articlesByQuery']['articles']['articles']

        for item in articles:
            item_url = DOMAIN_NAME + item['url']
            yield scrapy.Request(url=get_proxy_url(item_url), callback=self.scrape, cb_kwargs={'url': item_url})

    def scrape(self, response, url):
        yield {
            'title': response.css('h1.font-georgia.text-4xl::text').get(),
            'author': response.css('span.font-source-sans.font-semibold.text-gray-700 a::text').get(),
            'location': '',
            'datetime': response.css('span.pr-3.font-source-sans.text-gray-700').xpath('./time/@datetime').get(),
            'content': response.css('div#content-wrap p::text').getall(),
            'url': url,
        }

    def req_config(self, curr_page):
        page = curr_page
        form_data = {
            "operationName": "ARTICLES_BY_QUERY",
            "variables": {
                "query": "ramadan bazaar",
                "locale": "EN",
                "page": page
            },
            "extensions": {},
            "query": "query ARTICLES_BY_QUERY($locale: LanguageType!, $query: String!, $page: Int) {\n  articlesByQuery(locale: $locale, query: $query, page: $page) {\n    query\n    articles {\n      summary {\n        totalItems\n        fromItems\n        toItems\n        currentPage\n        totalPages\n        __typename\n      }\n      articles {\n        title\n        excerpt\n        label {\n          name\n          slug\n          __typename\n        }\n        featuredImage {\n          url\n          altText\n          __typename\n        }\n        url\n        publishedAt\n        updatedAt\n        __typename\n      }\n      __typename\n    }\n    mostReadArticles {\n      title\n      excerpt\n      label {\n        name\n        slug\n        __typename\n      }\n      featuredImage {\n        url\n        altText\n        __typename\n      }\n      url\n      publishedAt\n      updatedAt\n      __typename\n    }\n    __typename\n  }\n}"
        }
        body = json.dumps(form_data)
        headers = {
            "Content-Type": "application/json",
        }

        return {
            'api_url': API_URL,
            'page': page,
            'form_data': form_data,
            'body': body,
            'headers': headers,
        }
    
    def get_total_pages(self, response):
        body = json.loads(response.body)
        total_pages = body['data']['articlesByQuery']['articles']['summary']['totalPages']
        return total_pages
