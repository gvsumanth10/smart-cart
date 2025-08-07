from playwright.sync_api import sync_playwright
import csv
import time
import re

# --- Configuration ---
ZEPTO_HOME_URL = "https://www.zeptonow.com/"
REALISTIC_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

KNOWN_BRANDS = [
    '24 Mantra',
    'Aashirvaad',
    'Aavin',
    'Akshayakalpa',
    'Amul',
    'Anand',
    'Annapurna',
    'Anveshan',
    'Aptamil',
    'Arokya',
    'B Natural',
    'Badshah',
    'Bertolli',
    'Better Nutrition',
    'Bhagyalakshmi',
    'Borges',
    'Britannia',
    'CRISTA',
    'Cadbury',
    'Catch',
    'Cavin\'s',
    'Chhapanbhog',
    'Ching\'s Secret',
    'Cinch Eats',
    'CookieMan',
    'Country Delight',
    'Cremeitalia',
    'D\'lecta',
    'Dabur',
    'Daily Good',
    'Dairy Craft',
    'Del Monte',
    'Delicious',
    'Dhara',
    'Didier & Frank',
    'Disano',
    'Dodla',
    'Double Horse',
    'Dukes',
    'Eastern',
    'Epigamia',
    'Everest',
    'Farmley',
    'Floryo',
    'Fortune',
    'Freedom',
    'Frooti',
    'Galaxy',
    'Gits',
    'Go Cheese',
    'Godrej Jersey',
    'Gold Winner',
    'Gowardhan',
    'Habanero',
    'Hatsun',
    'Heritage',
    'Hershey\'s',
    'Hocco',
    'India Gate',
    'Jivo',
    'KILRR',
    'Kapiva',
    'Karachi Bakery',
    'Kinder',
    'KitKat',
    'Kodai Cheese',
    'Knorr',
    'Lindt',
    'Luvit',
    'MOM',
    'MTR',
    'Maaza',
    'Maggi',
    'Malkist',
    'Max Protein',
    'Milky Mist',
    'Modern',
    'Mother Dairy',
    'Mother\'s Recipe',
    'Naga',
    'Nandini',
    'Natureland',
    'Nestle',
    'Nongshim',
    'Nova',
    'Nutralite',
    'Old Craft',
    'Open Secret',
    'Organic Tattva',
    'Palekar',
    'Paper Boat',
    'Parle',
    'Patanjali',
    'Pillsbury',
    'Popular Essentials',
    'Priya',
    'Puramate',
    'RIO',
    'Raajali',
    'Rani',
    'Raw Pressery',
    'Real Thai',
    'Right Shift',
    'Ritebite',
    'Rosier FOODs',
    'Sangam Dairy',
    'Shan',
    'Sid\'s Farm',
    'Slurrp Farm',
    'Smart One',
    'Storia',
    'Sugar free',
    'Sunfeast',
    'Surya',
    'Tata',
    'Tata Salt',
    'Tata Sampann',
    'The Belgian Waffle Co',
    'The Health Factory',
    'The Select Aisle',
    'Theobroma',
    'Toblerone',
    'Tropicana',
    'Two Brothers',
    'Unibic',
    'Unifit',
    'Vallombrosa',
    'Vijay',
    'Wakao',
    'Yakult',
    'YiPPee!',
    'Yu',
    'ZOFF',
    # Zepto's Private Brands
    'Daily Good',
    'Relish',
    'Zepto Essentials'
]

# --- Helper Functions ---
def extract_brand_from_name(product_name: str) -> str:
    for brand in KNOWN_BRANDS:
        if brand.lower() in product_name.lower():
            return brand
    return product_name.split(' ')[0]

def create_valid_filename(category_name: str) -> str:
    """Cleans a category name to make it a valid filename."""
    s = category_name.replace('&', 'and')
    s = re.sub(r'[^\w\s-]', '', s).strip()
    s = re.sub(r'[-\s]+', '_', s).lower()
    return f"{s}_products.csv"

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

# --- NEW: Helper function to handle intermittent errors ---
def handle_try_again(page):
    """Checks for a 'Try Again' button and clicks it if visible."""
    try:
        # Check for the button with a short timeout so we don't slow down normal runs
        try_again_button = page.get_by_label("Try Again").wait_for(state='visible', timeout=5000)
        if try_again_button.is_visible(timeout=5000): # Short 5-second check
            print("⚠️ 'Try Again' button detected. Clicking it...")
            try_again_button.click()
            # Wait for the page to reload after the click
            page.wait_for_load_state('load', timeout=30000)
            print("✅ Page reloaded after 'Try Again'.")
    except Exception:
        # If the button is not found or another error occurs, just continue silently
        pass


# --- Scraping Logic for a single sub-category page ---
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
            time.sleep(5) # A tiny delay between key presses
                
        time.sleep(2) # Wait for new items to load after scrolling

        for _ in range(10):
            page.keyboard.press('PageUp')
            time.sleep(2)  # A tiny delay to allow the page to load new items

        time.sleep(5) # Wait for initial products to settle
        
        page.keyboard.press('PageDown')
        for _ in range(20): # Press PageDown 20 times for a smooth scroll
            page.keyboard.press('PageDown')
            time.sleep(2) # A tiny delay between key presses
                
        time.sleep(2) # Wait for new items to load after scrolling


        while True:
            previous_total = len(scraped_product_urls)
            visible_cards = page.locator(product_card_selector).all()
            for card in visible_cards:
                try:
                    product_url = "https://www.zeptonow.com" + card.get_attribute('href')
                    if product_url in scraped_product_urls:
                        continue
                    
                    # Scrape all details
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
        print(f"❌ Timeout or error scraping {sub_category_name}: {e}")
    
    return product_list

# --- Main Execution ---
if __name__ == "__main__":
    with sync_playwright() as p:
        # For the final run, you can set headless=True to run it faster in the background
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=REALISTIC_USER_AGENT)
        page = context.new_page()
        
        try:
            print("--- STEP 1: Setting location ONCE for the entire session ---")
            page.goto(ZEPTO_HOME_URL, wait_until="load", timeout=90000)
            page.get_by_label("Select Location").click()
            location_input = page.get_by_placeholder("Search a new address")
            location_input.wait_for(timeout=15000)
            location_input.fill("Chennai")
            page.locator('[data-testid="address-search-item"]').first.click()
            page.locator('[data-testid="location-confirm-btn"]').click()
            print("✅ Location has been set.")
            page.wait_for_timeout(5000)

            print("\n--- STEP 2: Discovering all main categories from footer ---")
            # Use the data-testid from the HTML you provided to find the links 
            time.sleep(5)  # Wait for the page to load completely

            # Slowly scroll down by pressing 'PageDown' key
            print("Scrolling down...")
            time.sleep(5) # Wait for initial products to settle
            page.keyboard.press('PageDown')
            for _ in range(10): # Press PageDown 20 times for a smooth scroll
                page.keyboard.press('PageDown')
                time.sleep(0.75) # A tiny delay between key presses
                
            time.sleep(2) # Wait for new items to load after scrolling

            # Wait for the footer to be visible
            page.locator('footer').wait_for(state='visible', timeout=30000)
            footer = page.locator('footer').wait_for(state='visible', timeout=30000)
            print("Footer is now visible. Proceeding to scrape main categories...")
            
            # Find the H3 heading with the text "Categories" to be very specific
            category_list_selector = 'h3:has-text("Categories") + div ul'
            category_list_container = page.locator(category_list_selector)
            
            # Now, find all the links ONLY within that specific container
            main_category_links = category_list_container.locator('a').all()
            
            main_categories_to_scrape = []
            for link in main_category_links:
                name = link.locator('p').inner_text()
                href = link.get_attribute('href')
                main_categories_to_scrape.append({
                    'name': name,
                    'url': "https://www.zeptonow.com" + href
                })

            print(f"✅ Discovered {len(main_categories_to_scrape)} main categories to scrape.")
            for cat in main_categories_to_scrape:
                print(f"  - Found: {cat['name']}")
            
            # --- NEW: Filter out non-food categories ---
            food_categories_to_scrape = []
            non_food_categories = ["Makeup & Beauty", "Bath & Body", "Cleaning Essentials", "Home Needs", "Electricals & Accessories", "Hygiene & Grooming", "Health & Baby Care", "Paan Corner", "Pet Care", "Stationery & Office Supplies", "Gifts & Flowers", "Kitchen Essentials", "Home Decor", "Furniture & Furnishings", "Sports & Fitness", "Toys & Games", "Books & Magazines", "Automotive Accessories"]
            for link in main_category_links:
                try:
                    name = link.locator('p').inner_text(timeout=5000)
                    href = link.get_attribute('href',timeout=5000)
                    if name not in non_food_categories:
                        food_categories_to_scrape.append({
                            'name': name,
                            'url': "https://www.zeptonow.com" + href
                        })
                except Exception:
                    # If a link doesn't have a <p> tag or href, just ignore it and continue
                    print("Found a footer link that is not a category, gracefully skipping.")
                    continue


            print(f"✅ Discovered {len(food_categories_to_scrape)} food-related main categories to scrape.")
            for cat in food_categories_to_scrape:
                print(f"  - Found: {cat['name']}")

            # --- STEP 3: Loop Through Each Main Category and Scrape It ---
            for category in food_categories_to_scrape:
                main_category_name = category['name']
                main_category_url = category['url']
                all_products_in_category = []

                print(f"\n--- PROCESSING MAIN CATEGORY: {main_category_name.upper()} ---")
                
                page.goto(main_category_url, wait_until="load", timeout=90000)

                handle_try_again(page)

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

                for sub_cat in sub_categories_to_scrape:
                    products = scrape_subcategory_page(page, main_category_name, sub_cat)
                    all_products_in_category.extend(products)
                
                if all_products_in_category:
                    filename = create_valid_filename(main_category_name)
                    save_to_csv(all_products_in_category, filename)

        except Exception as e:
            print(f"❌ A major error occurred during the process: {e}")
            page.screenshot(path="main_error.png", full_page=True)
        finally:
            print("\nClosing browser...")
            browser.close()