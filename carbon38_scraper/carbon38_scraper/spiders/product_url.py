import scrapy
from scrapy.exceptions import CloseSpider


class ProductUrlSpider(scrapy.Spider):
    """
    Spider Name: product_urls

    Purpose:
        Crawls all product URLs from the Carbon38 Tops category.
        Automatically handles pagination and stores each product URL in a JSON Lines file.

    Output:
        - product_urls.jl: Contains one product URL per line in JSON format.

    How it works:
        1. Starts at the tops listing page.
        2. Extracts product page links from each page.
        3. Follows the "Next page" button until the last page is reached.
    """

    name = 'product_urls'
    allowed_domains = ['carbon38.com']
    start_urls = ['https://www.carbon38.com/shop-all-activewear/tops']


    def parse(self, response):
        """
        Extracts product URLs from the current page and follows pagination if available.
        """
        try:
            # Extract product card hrefs
            product_links = response.css('a.ProductItem__ImageWrapper.ProductItem__ImageWrapper--withAlternateImage::attr(href)').getall()

            if not product_links:
                self.logger.warning("No product links found on page: %s", response.url)

            for idx, link in enumerate(product_links, start=1):
                full_url = response.urljoin(link)
                self.logger.info(f"Product URL {idx}: {full_url}")
                yield {"product_url": full_url}

            # Follow the "Next page" link if it exists
            next_page = response.css('a.Pagination__NavItem.Link.Link--primary[title="Next page"]::attr(href)').get()
            if next_page:
                self.logger.info("Moving to next page...")
                yield response.follow(next_page, callback=self.parse)
            else:
                self.logger.info("All pages crawled. No further pagination found.")

        except Exception as e:
            self.logger.error(f" Error parsing {response.url}: {e}", exc_info=True)
            raise CloseSpider(reason=f"Spider crashed on {response.url}")
