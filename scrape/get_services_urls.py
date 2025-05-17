import json
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from collections import defaultdict

def scrape_all_categories():
    base_url = "https://digital.gov.eg/categories/"
    grouped_data = defaultdict(list)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url)

        # Wait for all category buttons
        page.wait_for_selector('button[id^="mainCategoryBtn-22"]')
        category_buttons = page.query_selector_all('button[id^="mainCategoryBtn-"]')

        for i, btn in enumerate(category_buttons):
            category_name = btn.inner_text()

            # Click the category button
            btn.click()
            page.wait_for_timeout(1000)

            links = page.query_selector_all('a[id^="categoryLink-"]')
            if not links:
                print(f"No active services in category: {i}")
                continue
            print(f"category {i} num links: {len(links)}")



            for link in links:
                href = link.get_attribute("href")
                full_url = urljoin(base_url, href)

                h2 = link.query_selector("h2")
                title = h2.inner_text() if h2 else ""

                grouped_data[category_name].append({
                    "title": title,
                    "url": full_url
                })
            
            print(f"==== category {i} done ====")


        browser.close()

    # Save to JSON file
    with open("services_by_category.json", "w", encoding="utf-8") as f:
        json.dump(grouped_data, f, ensure_ascii=False, indent=4)

    print("✅ Data saved to services_by_category.json")

# Run it
scrape_all_categories()
