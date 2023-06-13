from urllib.parse import urlencode
from dotenv import load_dotenv
import scrapy
import os
import json


load_dotenv()
PROXY_URL = os.environ["PROXY_URL"]
API_KEY = os.environ["API_KEY"]

DOMAIN_NAME = 'https://www.freemalaysiatoday.com'
API_URL = 'https://cms.freemalaysiatoday.com/graphql'

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = PROXY_URL + '?' + urlencode(payload)
    return proxy_url

class NewsSiteScraperSpider(scrapy.Spider):
    name = 'newssitescraperspider'

    def start_requests(self):
        config = self.req_config(curr_offset=0)
        yield scrapy.FormRequest(url=get_proxy_url(config['api_url']), method="POST", headers=config['headers'], body=config['body'], callback=self.parse)

    def parse(self, response):
        self.crawl(response)

        total = self.get_total_pages(response)

        if total > 10:
            for offset in range(10, total, 10):
                config = self.req_config(curr_offset=offset)
                yield scrapy.FormRequest(url=get_proxy_url(config['api_url']), method="POST", headers=config['headers'], body=config['body'], callback=self.crawl)

    def crawl(self, response):
        body = json.loads(response.body)
        edges = body['data']['posts']['edges']

        for item in edges:
            item_url = DOMAIN_NAME + item['node']['uri']
            item_date = item['node']['dateGmt']
            yield scrapy.Request(url=get_proxy_url(item_url), callback=self.scrape, cb_kwargs={'url': item_url, 'datetime': item_date})

    def scrape(self, response, url, datetime):
        yield {
            'title': response.css('h1.Page__PostTitleH1-sc-1auxjzz-0::text').get(),
            'author': response.css('span.author a.Style__StyledAnchor-sc-kwuyeg-0::text').get(),
            'location': '',
            'datetime': datetime,
            'content': response.css('div.Content__StyledDiv-sc-1n9vywj-0 p::text').getall(),
            'url': DOMAIN_NAME + url,
        }

    def req_config(self, curr_offset):
        offset = curr_offset
        form_data = {
            "query": '\n    query searchPosts {\n      \n      posts(\n        where: {\n          taxQuery: { taxArray: [{ terms: [\"top-news\",\"top-bm\",\"business\",\"local-business\",\"world-business\",\"nation\",\"sabahsarawak\",\"tempatan\",\"pandangan\",\"dunia\",\"column\",\"editorial\",\"letters\",\"fmt-worldviews\",\"world\",\"south-east-asia\",\"property\",\"sports\",\"football\",\"badminton\",\"motorsports\",\"tennis\",\"leisure\",\"top-lifestyle\",\"automotive\",\"simple-stories\",\"travel\",\"food\",\"entertainment\",\"money\",\"health\",\"pets\",\"education\"], operator: IN, taxonomy: CATEGORY, field: SLUG }], relation: AND },\nsearch: \"ramadan bazaar\",\noffsetPagination: {offset: ' + str(offset) + ', size: 10}\n        },\n        first: null,\n        after: \"\",\n        before: \"\",\n        last: null\n      ) {\n        \n        \n          pageInfo {\n            offsetPagination {\n              hasMore\n              hasPrevious\n              total\n            }\n          }\n        \n        edges {\n          node {\n            id\n            databaseId\n            slug\n            title\n            dateGmt\n            uri\n            excerpt\n            featuredImage {\n              node {\n                mediaItemUrl\n                \n              }\n            }\n            \n            \n    categories(first: 1, where: {\n      \n    }) {\n      nodes {\n        id\n        slug\n        name\n        uri\n      }\n    }\n  \n            \n          }\n        }\n      }\n    \n    }\n  ',
        }
        body = json.dumps(form_data)
        headers = {
            "Content-Type": "application/json",
        }

        return {
            'api_url': API_URL,
            'offset': offset,
            'form_data': form_data,
            'body': body,
            'headers': headers,
        }
    
    def get_total_pages(self, response):
        body = json.loads(response.body)
        total_pages = body['data']['posts']['pageInfo']['offsetPagination']['total']
        return total_pages
