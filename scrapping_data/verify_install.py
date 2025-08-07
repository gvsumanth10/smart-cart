from playwright.sync_api import sync_playwright, Error

print("🚀 Attempting to launch a browser to verify installation...")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        print("✅ Success! Browser launched without errors.")
        browser.close()
        print("✅ Browser closed successfully. Your Playwright installation is working!")
except Error as e:
    print(f"❌ Failure! An error occurred: {e}")
    print("Please try running 'playwright install --with-deps' to fix it.")