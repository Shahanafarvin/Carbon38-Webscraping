# Carbon38 Web Scraper

This project scrapes product data from the Carbon38 website using Scrapy. It includes two spiders:

- `product_url.py`: Scrapes product page URLs from the category listing pages.
- `product_data.py`: Extracts detailed product information and review count from each product page.

## How It Works

1. Run the `product_url` spider to collect product URLs:`scrapy crawl product_url -o output/carbon38_urls.jl`


2. Run the `product_data` spider to collect detailed product data:`scrapy crawl product_data`

It extracts:
- Product name, brand, price
- Sizes, color, image URLs
- Description, fabric & care, size & fit
- Review count from the Yotpo API

## Project Structure

- `spiders/`
- `product_url.py`: Spider to scrape product page URLs
- `product_data.py`: Spider to scrape detailed product info and reviews
- `settings.py`: Scrapy project settings
- `output/`: Folder containing `.jl`, `.json`, and `.csv` outputs

## Requirements

- Python 3.x
- Scrapy

Install Scrapy if not already installed:`pip install scrapy`

