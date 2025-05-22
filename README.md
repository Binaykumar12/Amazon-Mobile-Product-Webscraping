# 📦 Amazon Mobile Scraper

A Python-based scraper that extracts mobile product data from [Amazon.in](https://www.amazon.in) including title, price, rating, reviews, availability, and a short description. Results are saved in both CSV and Excel formats with support for progress tracking, retry handling, and basic anti-bot techniques.

## 🚀 Features

- 🔍 Search any product (default: `mobile`)
- 📄 Scrapes up to N pages and M products (configurable)
- 📦 Extracts:
  - Product Title
  - Price
  - Rating
  - Review Count
  - Availability
  - Short Description
  - Product URL
- 🛡 Handles bot detection and retries
- ⏱ Adds random delays to mimic human behavior
- 📊 Saves results to CSV and Excel
- 📈 Displays real-time scraping progress with `tqdm`

## 📂 Example Output

Sample data saved in `amazon_results/`:

| Title                        | Price | Rating | Reviews |
|-----------------------------|-------|--------|---------|
| Samsung Galaxy M14 5G       | ₹12,490 | 4.2    | 15,000  |
| Redmi Note 12               | ₹13,999 | 4.3    | 9,800   |

## ⚙️ Configuration

Modify these variables at the top of the script:

```python
SEARCH_TERM = "mobile"   # Product to search
MAX_PAGES = 5            # Max Amazon search pages to scrape
MAX_PRODUCTS = 50        # Max number of product details to extract


🧰 Requirements
Install dependencies:

pip install requests beautifulsoup4 pandas tqdm openpyxl
▶️ Usage
Clone the repo and run:

python amazon_scraper.py
Results will be saved in amazon_results/ with timestamped filenames.

⚠️ Disclaimer
This script is for educational and personal research use only.
Scraping Amazon may violate their Terms of Service.
Use responsibly and avoid excessive requests.

📄 License
This project is open-source under the MIT License.
