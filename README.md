# news-site-scraper

This project is a news site crawler and scraper for sentiment analysis using Scrapy.

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file.

`API_KEY = <proxy_api_key>`

## Run Locally

Start scraping

```bash
  scrapy crawl <spider_name> [options]
```

Output in JSON format
```bash
  scrapy crawl <spider_name> -O output.json
```