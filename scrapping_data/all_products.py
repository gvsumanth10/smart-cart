from playwright.sync_api import sync_playwright
import csv
import time

# --- Configuration ---
MAIN_CATEGORY_URL = "https://www.zeptonow.com/cn/dairy-bread-eggs/cheese/cid/4b938e02-7bde-4479-bc0a-2b54cb6bd5f5/scid/f594b28a-4775-48ac-8840-b9030229ff87"
OUTPUT_FILENAME = "dairy_bread_eggs_full_catalogue.csv"
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

# --- Main Scraping Logic for a single sub-category page ---
def scrape_subcategory_page(page, sub_category_info: dict) -> list[dict]:
    product_list = []
    scraped_product_urls = set()
    
    sub_category_name = sub_category_info['name']
    sub_category_url = sub_category_info['url']
    sub_category_image_url = sub_category_info['image_url']

    print(f"\n--- Scraping Sub-Category: {sub_category_name.upper()} ---")
    
    try:
        page.goto(sub_category_url, wait_until="load", timeout=90000)
        
        print("Waiting for initial product cards to load...")
        product_card_selector = 'a:has(div._container_c1j8m_3)'
        page.locator(product_card_selector).first.wait_for(timeout=30000)
        print("Initial product cards have loaded!")

        print("Scrolling and scraping all products in this sub-category...")
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
                        "main_category": "Dairy-Bread-Eggs", "sub_category": sub_category_name,
                        "sub_category_image_url": sub_category_image_url,
                        "product_name": product_name, "brand": brand, "price": price, 
                        "original_price": original_price, "quantity": quantity, "rating": rating, 
                        "stock_status": stock_status, "product_url": product_url, "image_url": image_url
                    })
                    scraped_product_urls.add(product_url)
                except Exception:
                    continue
            
            print(f"Total unique products scraped so far in '{sub_category_name}': {len(scraped_product_urls)}")
            
            if page.locator('footer').is_visible():
                print(f"Footer is visible. Ending scroll for {sub_category_name}.")
                break
            
            if len(scraped_product_urls) == previous_total:
                patience_counter += 1
                if patience_counter >= 3:
                    print(f"No new products found after 3 scrolls in {sub_category_name}.")
                    break
            else:
                patience_counter = 0

            # page.evaluate("window.scrollBy(0, 500)")
            # time.sleep(1)
            
    except Exception as e:
        print(f"❌ An error occurred while scraping {sub_category_name}: {e}")
        page.screenshot(path=f"error_{sub_category_name}.png", full_page=True)
    
    return product_list

# --- Main Execution ---
if __name__ == "__main__":
    all_products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=REALISTIC_USER_AGENT)
        page = context.new_page()
        
        try:
            print("--- Setting location ONCE for the entire session ---")
            page.goto(MAIN_CATEGORY_URL, wait_until="load", timeout=90000)
            page.get_by_label("Select Location").click()
            location_input = page.get_by_placeholder("Search a new address")
            location_input.wait_for(timeout=15000)
            location_input.fill("Chennai")
            page.locator('[data-testid="address-search-item"]').first.click()
            page.locator('[data-testid="location-confirm-btn"]').click()
            print("✅ Location has been set.")
            page.wait_for_timeout(5000)

            # --- PHASE 1: Discover Sub-Category Details ---
            print(f"\n--- Discovering sub-categories within '{MAIN_CATEGORY_URL.split('/')[-1]}' ---")
            # This selector finds the container for the sub-category links from your HTML
            sub_category_container_selector = 'div.no-scrollbar.sticky'
            sub_category_links = page.locator(f'{sub_category_container_selector} a').all()
            
            sub_categories_to_scrape = []
            for link in sub_category_links:
                href = link.get_attribute('href')
                name = link.locator('p').inner_text()
                image_url = link.locator('img').get_attribute('src')
                if href and name:
                    full_url = "https://www.zeptonow.com" + href
                    sub_categories_to_scrape.append({'name': name, 'url': full_url, 'image_url': image_url})
            
            print(f"✅ Discovered {len(sub_categories_to_scrape)} sub-categories to scrape.")
            for sc in sub_categories_to_scrape:
                print(f"  - Found: {sc['name']}")

            # --- PHASE 2: Loop through each discovered sub-category and scrape it ---
            for sub_category in sub_categories_to_scrape:
                products_from_category = scrape_subcategory_page(page, sub_category)
                all_products.extend(products_from_category)
                print(f"--- Finished sub-category '{sub_category['name']}'. Total products collected so far: {len(all_products)} ---")

        except Exception as e:
            print(f"❌ A major error occurred during setup or discovery: {e}")
            page.screenshot(path="main_error.png", full_page=True)

        finally:
            print("\nClosing browser...")
            browser.close()

    # --- Save all collected data to a single CSV file ---
    if all_products:
        print(f"\n💾 Saving a total of {len(all_products)} products to '{OUTPUT_FILENAME}'...")
        with open(OUTPUT_FILENAME, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = [
                "main_category", "sub_category", "sub_category_image_url", "product_name", 
                "brand", "price", "original_price", "quantity", "rating", 
                "stock_status", "product_url", "image_url"
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_products)
        print("✅ Done! Your complete category catalogue is ready.")
    else:
        print("\nNo products were scraped.")