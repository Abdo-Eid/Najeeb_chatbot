from playwright.sync_api import sync_playwright

url = "https://digital.gov.eg/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set headless=False to see the browser
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector(".logo-spin", state="detached")


    # Use XPath to locate the element
    elements = page.locator('//html/body/main/div[1]/div/div/h1')

    if elements.count() > 0:
        print("Extracted Item:", elements.nth(0).inner_text())
    else:
        print("Item not found.")

    browser.close()
