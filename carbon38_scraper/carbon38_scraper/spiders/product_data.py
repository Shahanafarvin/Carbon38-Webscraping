import json
import scrapy
from scrapy.http import Response, Request


class ProductDetailSpider(scrapy.Spider):
    """
    Spider Name: product_data

    Purpose:
        - Scrapes detailed product information and review counts from carbon38.com.
        - Combines web scraping with an external API call (Yotpo) for enriched data.

    Input:
        - Reads product URLs from `output/carbon38_urls.jl`.

    Output:
        - Yields a dictionary containing product attributes and Yotpo review counts.
    """
    name = 'product_data'
    allowed_domains = ['carbon38.com']

    def start_requests(self):
        """
        Reads product URLs from a JSON Lines file and starts the scraping process.

        Raises:
            FileNotFoundError: If the input file does not exist.
            Exception: For any other issues while reading the file.
        """
        file_path = 'output/carbon38_urls.jl'
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    data = json.loads(line)
                    url = data.get('product_url')
                    if url:
                        self.logger.info(f"🔗 Crawling product: {url}")
                        yield scrapy.Request(url=url, callback=self.parse_product)
        except FileNotFoundError:
            self.logger.error(f"❌ File '{file_path}' not found. Run 'product_url_spider' first.")
        except Exception as e:
            self.logger.error(f"❌ Error reading '{file_path}': {e}", exc_info=True)

    def add_https(self, url: str) -> str:
        """
        Ensures the URL has HTTPS schema.

        Args:
            url (str): Partial or full image URL.

        Returns:
            str: Complete URL with HTTPS schema.
        """
        return f"https:{url}" if url and url.startswith("//") else url

    def parse_faq_data(self, response: Response) -> dict:
        """
        Extracts FAQ section data such as "Editor's Notes", "Size & Fit", and "Fabric & Care".

        Args:
            response (scrapy.http.Response): HTML response object.

        Returns:
            dict: Mapping of FAQ questions to their respective answers.
        """
        faq_section = response.css('section[data-section-type="faq"] div.Faq__ItemWrapper')
        faq_data = {}
        for item in faq_section:
            question = item.css('button.Faq__Question::text').get(default='').strip()
            answer_parts = item.css('div.Faq__AnswerWrapper p *::text').getall()
            answer = " ".join(text.strip() for text in answer_parts if text.strip())
            faq_data[question] = answer
        return faq_data

    def parse_product(self, response: Response):
        """
        Parses product page content and triggers Yotpo API call for review count.

        Args:
            response (scrapy.http.Response): Product page response.

        Yields:
            dict: Complete product information.
        """
        try:
            faq_data = self.parse_faq_data(response)

            product = {
                "product_url": response.url,
                "primary_image_url": self.add_https(
                    response.css('a.Product__SlideshowNavImage.AspectRatio > img::attr(src)').get(default="not found")
                ),
                "brand": response.css(
                'div.ProductMeta > h2.ProductMeta__Vendor.Heading.u-h1::text,div.ProductMeta > h2.ProductMeta__Vendor.Heading.u-h1 > a::text'
                ).get(default="not found"),
                "product_name": response.css('h1.ProductMeta__Title.Heading.u-h3::text').get(default="not found"),
                "price": response.css(
                    'span.ProductMeta__Price.Price::text'
                ).get(default="not found").replace('USD', '').strip(),
                "colour": response.css('span.ProductForm__SelectedValue ::text').get(default="not found"),
                "sizes": response.css(
                    'ul.SizeSwatchList.HorizontalList.HorizontalList--spacingTight > li > label::text'
                ).getall(),
                "description": faq_data.get("Editor's Notes", ""),
                "size_and_fit": faq_data.get("Size & Fit", ""),
                "fabric&care": faq_data.get("Fabric & Care", ""),
                "image_urls": [
                    self.add_https(url)
                    for url in response.css(
                        'a.Product__SlideshowNavImage.AspectRatio > img::attr(src)'
                    ).getall()
                ],
            }

            # Call separate function to handle review scraping
            yield from self.fetch_review_data(response, product)

        except Exception as e:
            self.logger.error(f"❌ Error parsing product page {response.url}: {e}", exc_info=True)

    def fetch_review_data(self, response: Response, product: dict):
        """
        Extracts product ID and calls Yotpo API to fetch review count.

        Args:
            response (scrapy.http.Response): Original product response.
            product (dict): Parsed product information.

        Yields:
            Request or dict: If Yotpo ID is present, yield API request;
                             else, yield product with 0 reviews.
        """
        product_id = response.css(
            'div.yotpo-widget-instance::attr(data-yotpo-product-id)'
        ).get()

        if product_id:
            store_id = "77OFfab03RDNwJXqpx5Bl5qmZJcAjybjX3EnuxBh"
            api_url = (
                f"https://api-cdn.yotpo.com/v3/storefront/store/{store_id}"
                f"/product/{product_id}/reviews?page=1&perPage=1"
            )
            yield scrapy.Request(
                url=api_url,
                callback=self.parse_reviews,
                meta={"item_data": product},
                dont_filter=True
            )
        else:
            self.logger.warning(f"⚠️ No Yotpo product ID found for: {response.url}")
            product["reviews"] = "0 Reviews"
            yield product

    def parse_reviews(self, response: Response):
        """
        Parses the Yotpo API response to extract total review count.

        Args:
            response (scrapy.http.Response): Yotpo API response.

        Yields:
            dict: Product data with the `reviews` field added.
        """
        item = response.meta.get("item_data", {})
        try:
            data = json.loads(response.text)
            review_count = data.get("pagination", {}).get("total", 0)
            item["reviews"] = f"{review_count} Reviews"
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to parse Yotpo response: {e}")
            item["reviews"] = "0 Reviews"

        yield item
