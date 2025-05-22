import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from tqdm import tqdm

# Configuration
SEARCH_TERM = "mobile"
BASE_URL = "https://www.amazon.in"
MAX_PAGES = 5  # Number of search pages to scrape
MAX_PRODUCTS = 50  # Maximum number of products to scrape

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.amazon.in/",
}

def get_amazon_page(url):
    """Handle requests with retries and delays"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random delay to avoid bot detection
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                if "captcha" in response.text.lower() or "rush hour" in response.text.lower():
                    print(f"⚠️ Amazon bot detection triggered on attempt {attempt+1}. Retrying...")
                    time.sleep(random.uniform(5, 10))  # Longer delay before retry
                    continue
                return response
            else:
                print(f"Request failed with status code: {response.status_code} on attempt {attempt+1}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))  # Wait before retry
                    continue
                return None
                
        except Exception as e:
            print(f"Request error on attempt {attempt+1}: {str(e)}")
            # Fix URL if it contains https:// prefix issues
            if "Failed to resolve 'www.amazon.inhttps'" in str(e):
                url = url.replace("www.amazon.inhttps", "www.amazon.in")
                print(f"Fixed malformed URL, retrying...")
                continue
            
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))  # Wait before retry
                continue
            return None
    
    return None

def extract_product_details(product_soup, url):
    """Extract product details with enhanced error handling"""
    try:
        # Extract title
        title = product_soup.find("span", id="productTitle")
        title = title.text.strip() if title else "N/A"
        
        # Extract price - try multiple selectors
        price = "N/A"
        price_whole = product_soup.find("span", class_="a-price-whole")
        if price_whole:
            price = price_whole.text.strip()
        else:
            # Try alternative price selectors
            price_element = product_soup.select_one("span.a-offscreen")
            if price_element:
                price = price_element.text.strip().replace("₹", "")
        
        # Extract rating
        rating = product_soup.find("span", class_="a-icon-alt")
        rating = rating.text.split()[0] if rating else "N/A"
        
        # Extract review count
        review_count = "N/A"
        reviews = product_soup.select_one("span#acrCustomerReviewText")
        if reviews:
            review_count = reviews.text.strip().split()[0].replace(",", "")
        
        # Extract availability
        availability = "In Stock"
        availability_elem = product_soup.select_one("#availability span")
        if availability_elem:
            availability = availability_elem.text.strip()
        
        # Extract description (limited)
        description = "N/A"
        desc_elem = product_soup.select_one("#feature-bullets .a-list-item")
        if desc_elem:
            description = desc_elem.text.strip()[:100] + "..." if len(desc_elem.text.strip()) > 100 else desc_elem.text.strip()
        
        return {
            "title": title[:80] + "..." if len(title) > 80 else title,
            "price": f"₹{price}" if price != "N/A" else price,
            "rating": rating,
            "reviews": review_count,
            "availability": availability,
            "description": description,
            "url": url
        }
        
    except Exception as e:
        print(f"Error extracting product details: {str(e)}")
        return None

def scrape_amazon_products():
    print(f"🔍 Searching for '{SEARCH_TERM}' on Amazon.in")
    all_products = []
    
    for page_num in range(1, MAX_PAGES + 1):
        # Construct search URL with page number
        if page_num == 1:
            search_url = f"{BASE_URL}/s?k={SEARCH_TERM.replace(' ', '+')}"
        else:
            search_url = f"{BASE_URL}/s?k={SEARCH_TERM.replace(' ', '+')}&page={page_num}"
        
        print(f"\n📄 Processing page {page_num}/{MAX_PAGES}...")
        
        # Get search page
        search_page = get_amazon_page(search_url)
        if not search_page:
            print(f"❌ Failed to fetch page {page_num}. Moving to next page if available.")
            continue
        
        soup = BeautifulSoup(search_page.content, "html.parser")
        
        # Find product links - updated selector for broader coverage
        product_links = []
        
        # Try multiple selectors for better coverage
        link_elements = soup.select("a.a-link-normal.s-no-outline[href*='/dp/']")
        if not link_elements:
            link_elements = soup.select("a.a-link-normal[href*='/dp/']")
        
        for link in link_elements:
            # Extract product URL and clean it
            href = link.get('href', '')
            if '/dp/' in href:
                product_url = href.split('/ref=')[0] if '/ref=' in href else href
                product_url = product_url.split('?')[0] if '?' in product_url else product_url
                
                # Make sure URL is absolute
                if not product_url.startswith('http'):
                    product_url = BASE_URL + product_url
                
                # Avoid duplicates
                if product_url not in [p['url'] for p in all_products] and product_url not in product_links:
                    product_links.append(product_url)
        
        print(f"📦 Found {len(product_links)} products on this page")
        
        # Scrape each product with progress bar
        with tqdm(total=len(product_links), desc="Scraping products", unit="item") as pbar:
            for url in product_links:
                # Stop if we've reached the maximum number of products
                if len(all_products) >= MAX_PRODUCTS:
                    print(f"✅ Reached maximum product limit ({MAX_PRODUCTS})")
                    break
                
                product_page = get_amazon_page(url)
                if not product_page:
                    pbar.update(1)
                    continue
                
                product_soup = BeautifulSoup(product_page.content, "html.parser")
                product_data = extract_product_details(product_soup, url)
                
                if product_data:
                    all_products.append(product_data)
                    pbar.set_description(f"Scraped: {product_data['title'][:30]}...")
                
                pbar.update(1)
        
        # Stop if we've reached the maximum number of products
        if len(all_products) >= MAX_PRODUCTS:
            break
        
        # Random delay between pages
        if page_num < MAX_PAGES:
            delay = random.uniform(5, 10)
            print(f"⏳ Waiting {delay:.1f} seconds before next page...")
            time.sleep(delay)
    
    return all_products

def format_table(df):
    """Format the dataframe for better display"""
    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'center')
    return df

if __name__ == "__main__":
    print("🚀 Starting Enhanced Amazon Scraper...")
    print(f"⚙️ Configuration: Search term: '{SEARCH_TERM}', Max pages: {MAX_PAGES}, Max products: {MAX_PRODUCTS}")
    
    # Create output directory if it doesn't exist
    output_dir = "amazon_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Start timer
    start_time = time.time()
    
    # Run scraper
    products = scrape_amazon_products()
    
    # End timer
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if products:
        df = pd.DataFrame(products)
        
        # Format and display results
        formatted_df = format_table(df)
        
        print("\n📋 Results Summary:")
        print(f"Total products scraped: {len(products)}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        
        # Show sample of results (first 10 rows with selected columns)
        display_cols = ['title', 'price', 'rating', 'reviews']
        print("\n📊 Sample Results:")
        sample_df = formatted_df[display_cols].head(10)
        print(sample_df.to_string(index=False))
        
        # Save to CSV with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{output_dir}/amazon_{SEARCH_TERM}_{timestamp}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\n💾 Saved full results to '{csv_filename}'")
        
        # Save to Excel for better formatting
        excel_filename = f"{output_dir}/amazon_{SEARCH_TERM}_{timestamp}.xlsx"
        try:
            df.to_excel(excel_filename, index=False, sheet_name=f"Amazon {SEARCH_TERM}")
            print(f"📊 Saved formatted results to '{excel_filename}'")
        except Exception as e:
            print(f"⚠️ Could not save Excel file: {str(e)}")
    else:
        print("❌ No products found or scraping failed.")
    
    print("\n✅ Scraping complete!")