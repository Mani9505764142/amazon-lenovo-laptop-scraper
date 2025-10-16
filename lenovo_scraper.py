import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

lenovo_laptops = []
page_num = 1
max_errors = 3
consecutive_errors = 0

while True:
    try:
        print(f"Scraping page {page_num}...")
        
        url = f'https://www.amazon.in/s?k=Lenovo+Laptop&page={page_num}'
        response = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        if not products:
            print("No more products found. Scraping complete!")
            break
        
        consecutive_errors = 0
        
        for product in products:
            try:
                title = product.find('h2').text.strip()
                
                # Filter: Only include if title contains "Lenovo" (case-insensitive)
                if 'lenovo' not in title.lower():
                    continue  # Skip non-Lenovo products
                
                # Price
                try:
                    price = product.find('span', 'a-price-whole').text
                    currency = '₹'
                    full_price = currency + price
                except:
                    full_price = 'Price not available'
                
                # Rating
                try:
                    rating = product.find('span', 'a-icon-alt').text
                except:
                    rating = 'No rating'
                
                # Product link
                link = product.find('a', 'a-link-normal')['href']
                full_link = 'https://www.amazon.in' + link
                
                # Image
                try:
                    image = product.find('img', 's-image')['src']
                except:
                    image = 'No image'
                
                lenovo_laptops.append({
                    'Title': title,
                    'Price': full_price,
                    'Rating': rating,
                    'Link': full_link,
                    'Image': image
                })
                
            except:
                continue
        
        print(f"Scraped {len(products)} products from page {page_num}")
        time.sleep(random.uniform(3, 7))
        page_num += 1
        
    except requests.exceptions.ConnectionError as e:
        consecutive_errors += 1
        print(f"Connection error on page {page_num}: {e}")
        print(f"Waiting 30 seconds before retry... (Error {consecutive_errors}/{max_errors})")
        
        if consecutive_errors >= max_errors:
            print("Too many consecutive errors. Saving data and stopping.")
            break
        
        time.sleep(30)
        
    except Exception as e:
        consecutive_errors += 1
        print(f"Error on page {page_num}: {e}")
        
        if consecutive_errors >= max_errors:
            print("Too many consecutive errors. Saving data and stopping.")
            break
        
        time.sleep(10)

# Save to CSV
with open('lenovo_only_laptops.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Title', 'Price', 'Rating', 'Link', 'Image'])
    writer.writeheader()
    writer.writerows(lenovo_laptops)

print(f'\nTotal Lenovo laptops scraped: {len(lenovo_laptops)}')
print('Data saved to lenovo_only_laptops.csv')
