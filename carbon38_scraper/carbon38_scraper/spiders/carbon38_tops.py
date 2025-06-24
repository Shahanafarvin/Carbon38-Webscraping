import scrapy

class Carbon38TopsSpider(scrapy.Spider):
    name = "carbon38_tops"
    allowed_domains = ["carbon38.com"]
    start_urls = ["https://carbon38.com/collections/tops?page=1"]

    def __init__(self):
        self.product_urls = []

    def parse(self, response):
        # Extract product URLs from the page
        links = response.css('a.ProductItem__ImageWrapper.ProductItem__ImageWrapper--withAlternateImage::attr(href)').getall()
        full_urls = [response.urljoin(link) for link in links]
        self.product_urls.extend(full_urls)

        # Print URLs from this page (for checking)
        print(f"Found {len(full_urls)} product URLs on page: {response.url}")

        # Go to next page if pagination exists
        next_page = response.css('a.Pagination__NavItem.Link.Link--primary[title="Next page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            # Save URLs to a file when all pages are scraped
            with open("product_urls.txt", "w") as f:
                for url in self.product_urls:
                    f.write(url + "\n")
