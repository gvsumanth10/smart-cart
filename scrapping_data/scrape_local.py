from playwright.sync_api import sync_playwright
import json
import csv
import time

MILK_CATEGORY_URL = "https://www.zeptonow.com/cn/dairy-bread-eggs/milk/cid/4b938e02-7bde-4479-bc0a-2b54cb6bd5f5/scid/22964a2b-0439-4236-9950-0d71b532b243"

OUTPUT_FILENAME = "milk_product_catalogue_detailed.csv"
REALISTIC_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

KNOWN_BRANDS = [
    'Akshayakalpa', 'Godrej Jersey', 'Sid\'s Farm', 'Arokya', 'Nandini', 'Aavin',
    'Amul', 'Heritage', 'Dodla', 'Country Delight', 'Milky Mist', 'Cavin\'s', 'Nestle', 'Amulya', 'Vallombrosa', 'Dairy Craft', 'Patanjali', 'Bangalore Milk', 'Sangam Dairy'
]

def extract_brand_from_name(product_name: str) -> str:
    for brand in KNOWN_BRANDS:
        if brand.lower() in product_name.lower():
            return brand
    return product_name.split(' ')[0]

def scrape_full_product_details(url: str) -> list[dict]:
    product_list = []
    scraped_product_urls = set()

    print("🚀 Starting local Playwright with SLOW SCROLLING method...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(user_agent=REALISTIC_USER_AGENT)
        page = context.new_page()
        
        try:
            print(f"Navigating to: {url}")
            # Increased timeout to 90 seconds for initial load
            page.goto(url, wait_until="load", timeout=90000)

            print("STEP 1: Handling location selection...")
            page.get_by_label("Select Location").click()
            location_input = page.get_by_placeholder("Search a new address")
            location_input.wait_for(timeout=15000)
            location_input.fill("Chennai")

            first_result_selector = '[data-testid="address-search-item"]'
            page.wait_for_selector(first_result_selector, timeout=15000)
            page.locator(first_result_selector).first.click()

            confirm_button_selector = '[data-testid="location-confirm-btn"]'
            page.wait_for_selector(confirm_button_selector, timeout=15000)
            page.locator(confirm_button_selector).click()
            
            print("Location confirmed. Waiting for initial product cards to load...")
            product_card_selector = 'a:has(div._container_c1j8m_3)'
            page.locator(product_card_selector).first.wait_for(timeout=30000)
            print("Initial product cards have loaded!")

            # --- NEW: SLOW SCROLLING & PATIENCE LOOP ---
            print("STEP 2: Slowly scrolling and scraping all products...")
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
                previous_total = len(product_list)
                
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
                            "product_name": product_name, "brand": brand, "price": price, "original_price": original_price,
                            "quantity": quantity, "rating": rating, "stock_status": stock_status,
                            "product_url": product_url, "image_url": image_url
                        })
                        
                        scraped_product_urls.add(product_url)
                    except Exception:
                        continue
                
                print(f"Total unique products scraped so far: {len(product_list)}")
                
                # Check if we should stop scrolling
                if len(product_list) == previous_total:
                    patience_counter += 1
                    if patience_counter >= 3: # Stop after 3 tries with no new products
                        print("Reached the bottom of the page. No more new products found.")
                        break
                else:
                    patience_counter = 0 # Reset patience if we found new products



            print(f"✅ Scraping complete! Total unique products found: {len(product_list)}")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            page.screenshot(path="local_error_screenshot.png", full_page=True)
            print(f"📸 Screenshot saved to 'local_error_screenshot.png'.")
        
        finally:
            print("Closing browser...")
            browser.close()
            
    return product_list

def save_to_csv(products: list[dict], filename: str):
    if not products:
        print("\nNo product data was scraped.")
        return
    print(f"\n💾 Saving {len(products)} products to '{filename}'...")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = [
            "product_name", "brand", "price", "original_price", "quantity", 
            "rating", "stock_status", "product_url", "image_url"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    print("✅ Done! Your detailed product catalogue is ready.")


if __name__ == "__main__":
    scraped_data = scrape_full_product_details(MILK_CATEGORY_URL)
    save_to_csv(scraped_data, OUTPUT_FILENAME)