import scrapy
import json


class ProductDetailSpider(scrapy.Spider):
    """
    Spider Name: product_data

    Purpose:
        This spider reads product URLs from `product_urls.jl` and scrapes detailed product data
        from each page on Carbon38.

    Inputs:
        - product_urls.jl: JSON Lines file containing {"product_url": "<url>"} lines

    Outputs:
        - output.json and output.csv: Detailed product data in structured format
    """

    name = 'product_data'
    allowed_domains = ['carbon38.com']
    
    def start_requests(self):
        """
        Read product URLs from a file and yield requests to each product page.
        """
        try:
            with open('output/carbon38_urls.jl', 'r') as file:
                for line in file:
                    data = json.loads(line)
                    url = data.get('product_url')
                    if url:
                        self.logger.info(f"🔗 Crawling product: {url}")
                        yield scrapy.Request(url=url, callback=self.parse_product)
        except FileNotFoundError:
            self.logger.error("❌ File 'product_urls.jl' not found. Run 'product_url_spider' first.")
        except Exception as e:
            self.logger.error(f"❌ Error reading product_urls.jl: {e}", exc_info=True)

    def add_https(self,url):
        if url and url.startswith("//"):
            return "https:" + url
        return url

    def parse_product(self, response):
        """
        Parse each product page and extract relevant fields.
        """

        faq_items = response.css('section[data-section-type="faq"] div.Faq__ItemWrapper')
        faq_data = {}

        for item in faq_items:
            question = item.css('button.Faq__Question::text').get(default='').strip()
            answer_parts = item.css('div.Faq__AnswerWrapper p *::text').getall()
            answer = " ".join(part.strip() for part in answer_parts if part.strip())
            faq_data[question] = answer

        try:
            yield {
            
            "primary_image_url": self.add_https(response.css('a.Product__SlideshowNavImage.AspectRatio > img::attr(src)').get()),
            "brand": response.css('div.ProductMeta > h2.ProductMeta__Vendor.Heading.u-h1 > a::text').get(default="not found"),
            "product_name": response.css('h1.ProductMeta__Title.Heading.u-h3::text').get(),
            "price": response.css('span.ProductMeta__Price.Price::text').get().replace('USD', '').strip(),
            "reviews": response.css('#yotpo-app > div > div > div > div:nth-child(2) > div.yotpo-header-container > div > div.yotpo-bottom-line > div > div > div.yotpo-bottom-line-right-panel > div.yotpo-bottom-line-text > div::text').get(default="0 Reviews").strip(),
            "colour": response.css('span.ProductForm__SelectedValue ::text').get(),
            "sizes": response.css('ul.SizeSwatchList.HorizontalList.HorizontalList--spacingTight > li > label::text').getall(),
            "description": faq_data.get("Editor's Notes", ""),
            "size_and_fit": faq_data.get("Size & Fit", ""),
            "fabric&care": faq_data.get("Fabric & Care", ""),
            "product_url": response.url,
            "image_urls": [
                    self.add_https(url) for url in response.css('a.Product__SlideshowNavImage.AspectRatio > img::attr(src)').getall()
            ],
            }

        except Exception as e:
            self.logger.error(f"❌ Error parsing product page {response.url}: {e}", exc_info=True)
