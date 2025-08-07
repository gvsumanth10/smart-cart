from playwright.sync_api import sync_playwright
import csv
import time
import re

# --- Configuration ---
ZEPTO_HOME_URL = "https://www.zeptonow.com/"
# No output filename here, as it will be generated dynamically
REALISTIC_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

KNOWN_BRANDS = [
    'Akshayakalpa', 'Godrej Jersey', 'Sid\'s Farm', 'Arokya', 'Nandini', 'Aavin',
    'Amul', 'Heritage', 'Dodla', 'Country Delight', 'Milky Mist', 'Cavin\'s', 'Nestle',
    'Amulya', 'Vallombrosa', 'Dairy Craft', 'Patanjali', 'Bangalore Milk', 'Sangam Dairy'
]

# --- Helper Functions ---
def extract_brand_from_name(product_name: str) -> str:
    for brand in KNOWN_BRANDS:
        if brand.lower() in product_name.lower():
            return brand
    return product_name.split(' ')[0]

def create_valid_filename(category_name: str) -> str:
    """Cleans a category name to make it a valid filename."""
    # Replace '&' with 'and', remove special characters, replace spaces with underscores
    s = category_name.replace('&', 'and')
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', '_', s).lower()
    return f"{s}.csv"

# --- Main Scraping Logic for a single sub-category page ---
def scrape_subcategory_page(page, main_category_name: str, sub_category_info: dict) -> list[dict]:
    # ... (This function is nearly identical to the previous version)
    # The full code for this function is included in the complete script below.
    pass # Placeholder for brevity here

# --- Save to CSV Function ---
def save_to_csv(products: list[dict], filename: str):
    if not products:
        print(f"\nNo products found to save for {filename}.")
        return
    print(f"\n💾 Saving {len(products)} products to '{filename}'...")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = [
            "main_category", "sub_category", "sub_category_image_url", "product_name", 
            "brand", "price", "original_price", "quantity", "rating", 
            "stock_status", "product_url", "image_url"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    print(f"✅ Done! Catalogue '{filename}' is ready.")

# --- Main Execution ---
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=REALISTIC_USER_AGENT)
        page = context.new_page()
        
        try:
            # --- Set location ONCE at the beginning ---
            print("--- STEP 1: Setting location for the entire session ---")
            page.goto(ZEPTO_HOME_URL, wait_until="load", timeout=90000)
            page.get_by_label("Select Location").click()
            location_input = page.get_by_placeholder("Search a new address")
            location_input.wait_for(timeout=15000)
            location_input.fill("Chennai")
            page.locator('[data-testid="address-search-item"]').first.click()
            page.locator('[data-testid="location-confirm-btn"]').click()
            print("✅ Location has been set.")
            page.wait_for_timeout(5000)

            # --- STEP 2: Discover All Main Categories from Footer ---
            print("\n--- STEP 2: Discovering all main categories from footer ---")
            main_category_links = page.locator('a[data-testid$="-footer-link"]').all()
            
            main_categories_to_scrape = []
            for link in main_category_links:
                name = link.locator('p').inner_text()
                href = link.get_attribute('href')
                # We only want food-related categories, so we can filter out others
                if name not in ["Makeup & Beauty", "Bath & Body", "Cleaning Essentials", "Home Needs", "Electricals & Accessories", "Hygiene & Grooming", "Health & Baby Care"]:
                    main_categories_to_scrape.append({
                        'name': name,
                        'url': "https://www.zeptonow.com" + href
                    })

            print(f"✅ Discovered {len(main_categories_to_scrape)} main categories to scrape.")
            for cat in main_categories_to_scrape:
                print(f"  - Found: {cat['name']}")

            # --- STEP 3: Loop Through Each Main Category and Scrape It ---
            for category in main_categories_to_scrape:
                main_category_name = category['name']
                main_category_url = category['url']
                all_products_in_category = []

                print(f"\n--- PROCESSING MAIN CATEGORY: {main_category_name.upper()} ---")
                
                # Discover sub-categories within this main category
                page.goto(main_category_url, wait_until="load", timeout=90000)
                sub_category_container_selector = 'div.no-scrollbar.sticky'
                sub_category_links = page.locator(f'{sub_category_container_selector} a').all()
                
                sub_categories_to_scrape = []
                for link in sub_category_links:
                    href = link.get_attribute('href')
                    name = link.locator('p').inner_text()
                    image_url = link.locator('img').get_attribute('src')
                    if href and name:
                        sub_categories_to_scrape.append({'name': name, 'url': "https://www.zeptonow.com" + href, 'image_url': image_url})
                
                print(f"Found {len(sub_categories_to_scrape)} sub-categories under {main_category_name}.")

                # Loop through and scrape each sub-category
                for sub_cat in sub_categories_to_scrape:
                    # Reusing the robust scraping logic from the previous script
                    # This function is defined below for completeness
                    products = scrape_subcategory_page(page, main_category_name, sub_cat)
                    all_products_in_category.extend(products)
                
                # Save all collected products for this main category to its own CSV
                if all_products_in_category:
                    filename = create_valid_filename(main_category_name)
                    save_to_csv(all_products_in_category, filename)

        except Exception as e:
            print(f"❌ A major error occurred during the process: {e}")
            page.screenshot(path="main_error.png", full_page=True)

        finally:
            print("\nClosing browser...")
            browser.close()


# This function is called by the main loop. It's the same robust scraper we built before.
def scrape_subcategory_page(page, main_category_name: str, sub_category_info: dict) -> list[dict]:
    product_list = []
    scraped_product_urls = set()
    
    sub_category_name = sub_category_info['name']
    sub_category_url = sub_category_info['url']
    sub_category_image_url = sub_category_info['image_url']

    print(f"\n--- Scraping Sub-Category: {sub_category_name.upper()} ---")
    
    try:
        page.goto(sub_category_url, wait_until="load", timeout=90000)
        
        product_card_selector = 'a:has(div._container_c1j8m_3)'
        page.locator(product_card_selector).first.wait_for(timeout=30000)

        patience_counter = 0
        # Slowly scroll down by pressing 'PageDown' key
        print("Scrolling down...")
        time.sleep(5) # Wait for initial products to settle
        page.keyboard.press('PageDown')
        for _ in range(10): # Press PageDown 20 times for a smooth scroll
            page.keyboard.press('PageDown')
            time.sleep(0.75) # A tiny delay between key presses
                
        time.sleep(2) # Wait for new items to load after scrolling
        
        while True:
            previous_total = len(scraped_product_urls)
            visible_cards = page.locator(product_card_selector).all()
            for card in visible_cards:
                try:
                    product_url = "https://www.zeptonow.com" + card.get_attribute('href')
                    if product_url in scraped_product_urls:
                        continue
                    
                    image_url = card.locator('img').get_attribute('src')
                    product_name = card.locator('div[data-slot-id="ProductName"]').inner_text()
                    quantity = card.locator('div[data-slot-id="PackSize"]').inner_text()
                    price = card.locator('div[data-slot-id="Price"] p').first.inner_text().replace('₹', '').strip()
                    rating_element = card.locator('div[data-slot-id="RatingInformation"]')
                    rating = rating_element.inner_text().replace('\n', ' ') if rating_element.is_visible() else "N/A"
                    brand = extract_brand_from_name(product_name)
                    original_price_element = card.locator('p[class*="_original-price"]')
                    original_price = original_price_element.inner_text().replace('₹', '').strip() if original_price_element.is_visible() else price
                    stock_status = "Sold Out" if card.locator('text="Sold out"').is_visible() else "In Stock"

                    product_list.append({
                        "main_category": main_category_name, "sub_category": sub_category_name,
                        "sub_category_image_url": sub_category_image_url, "product_name": product_name, 
                        "brand": brand, "price": price, "original_price": original_price, 
                        "quantity": quantity, "rating": rating, "stock_status": stock_status, 
                        "product_url": product_url, "image_url": image_url
                    })
                    scraped_product_urls.add(product_url)
                except Exception:
                    continue
            
            print(f"Total unique products scraped in '{sub_category_name}': {len(scraped_product_urls)}")
            
            if page.locator('footer').is_visible():
                break
            
            if len(scraped_product_urls) == previous_total:
                patience_counter += 1
                if patience_counter >= 3:
                    break
            else:
                patience_counter = 0

            # page.evaluate("window.scrollBy(0, 500)")
            # time.sleep(1)
            
    except Exception as e:
        print(f"❌ Timeout or error scraping {sub_category_name}: {e}")
    
    return product_list