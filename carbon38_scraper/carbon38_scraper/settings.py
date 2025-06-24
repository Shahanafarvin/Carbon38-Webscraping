

BOT_NAME = "carbon38_scraper"

SPIDER_MODULES = ["carbon38_scraper.spiders"]
NEWSPIDER_MODULE = "carbon38_scraper.spiders"

# Add default headers
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

DOWNLOAD_DELAY = 3

FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = 'INFO'

#enable jsonlines output
FEEDS = {
    'output/carbon38_urls.jl': {
        'format': 'jsonlines',
        'encoding': 'utf8',
        'overwrite': True,
    }
}