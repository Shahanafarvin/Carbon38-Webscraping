

BOT_NAME = "carbon38_scraper"

SPIDER_MODULES = ["carbon38_scraper.spiders"]
NEWSPIDER_MODULE = "carbon38_scraper.spiders"

# Add default headers
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

logging_level = 'INFO'  # Set logging level to INFO

# Throttle to prevent system overload
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 3  # seconds

# Enable job directory to resume crawls after interruption
#JOBDIR = 'crawls/product_detail_resume'

# Enable both JSON and CSV output with file paths
FEEDS = {
    'output/carbon38_data.json': {
        'format': 'json',
        'encoding': 'utf8',
        'overwrite': True,
    },
    'output/carbon38_data.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'overwrite': True,
    },
}