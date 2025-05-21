## 📘 Scraping `digital.gov.eg`: Problem-Solution Sequence

---

# 🛠️ Phase 0: Early Attempts & Rendering Problems

### 1. ❌ Initial Approach: `requests_html` Fails to Render Content

### **Code Used**

```python
from requests_html import HTMLSession

session = HTMLSession()
url = "<https://digital.gov.eg/>"
response = session.get(url)
response.html.render()
item = response.html.xpath("/html/body/main/div[1]/div/div/h1", first=True)

```

### **Issue**

- `.render()` uses Pyppeteer internally to load JS content
- Pyppeteer Chromium **failed to download** due to a broken URL:
    
    ```
    OSError: Chromium downloadable not found at ...
    
    ```
    
- No maintained fork of `requests_html` is available
- Even if Chromium had been available, rendering was unreliable for modern JS frameworks (like React)

---

### 2. ✅ Migration to Playwright

### Initial Code

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("<https://digital.gov.eg>", wait_until="load")
    element = page.locator("//html/body/main/div[1]/div/div/h1")
    print(element.nth(0).inner_text())

```

### **New Problem**

- Using `wait_until="load"` finishes when **basic HTML is loaded**
- However, the **real content is rendered by JS after the loader disappears**
- Result: `element.nth(0)` returns nothing or raises an error
- The main element was **not found** even though the page was technically loaded

---

## 3. 🐛 Problem: Playwright Hangs on `networkidle` Due to Persistent Loader

### 📌 Context

While scraping `https://digital.gov.eg/` using Playwright, the script would hang indefinitely when using:

```python
page.goto("<https://digital.gov.eg>", wait_until="networkidle")

```

### 🧠 Root Cause

The page includes a **JavaScript-based loader animation** (`<BarLoader>` from `react-spinners`) which:

- **Keeps the network busy** with ongoing requests (e.g. polling, animation intervals)
- Prevents the `networkidle` state from being reached
- Causes `goto(..., wait_until="networkidle")` to **hang forever**

### 🔍 Investigation

- A 900ms delay allowed the **main content to be visible**
- Capturing the network logs showed a file named:
    
    ```
    loading-2c24ada4a968d3cf.js
    
    ```
    
- This confirmed a persistent loading mechanism tied to frontend rendering

---

## ✅ Solution: Wait for Loader to Disappear via Selector

### Selector Identified

The loader is rendered inside:

```html
<div class="logo-spin">...</div>

```

### Fix in Code

Replace `networkidle` with:

```python
page.goto("<https://digital.gov.eg>")
page.wait_for_selector(".logo-spin", state="detached")  # wait until loader is gone

```

---

## ✅ Outcome

- Page content loads fully
- Loader disappears
- DOM elements become available for scraping
- No hanging or false negatives

## omar notes

### 📘 Scraping `digital.gov.eg`: Problem-Solution Sequence

---

### 1. ❌ Initial Approach: `requests_html` Fails to Render Content

### **Code Used**

```python
from requests_html import HTMLSession

session = HTMLSession()
url = "<https://digital.gov.eg/>"
response = session.get(url)
response.html.render()
item = response.html.xpath("/html/body/main/div[1]/div/div/h1", first=True)

```

### **Issue**

- `.render()` uses Pyppeteer internally to load JS content
- Pyppeteer Chromium **failed to download** due to a broken URL:
    
    ```python
    OSError: Chromium downloadable not found at ...
    
    ```
    
- No maintained fork of `requests_html` is available
- Even if Chromium had been available, rendering was unreliable for modern JS frameworks (like React)

---

### 2. ✅ Migration to Playwright

### **Initial Code**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("<https://digital.gov.eg>", wait_until="load")
    element = page.locator("//html/body/main/div[1]/div/div/h1")
    print(element.nth(0).inner_text())

```

### **New Problem**

- Using `wait_until="load"` finishes when **basic HTML is loaded**
- However, the **real content is rendered by JS after the loader disappears**
- Result: `element.nth(0)` returns nothing or raises an error
- The main element was **not found** even though the page was technically loaded

---

## 3. 🐛 Problem: Playwright Hangs on `networkidle` Due to Persistent Loader

### 📌 Context

While scraping `https://digital.gov.eg/` using Playwright, the script would hang indefinitely when using:

```python
page.goto("<https://digital.gov.eg>", wait_until="networkidle")

```

### 🧠 Root Cause

The page includes a **JavaScript-based loader animation** (`<BarLoader>` from `react-spinners`) which:

- **Keeps the network busy** with ongoing requests (e.g. polling, animation intervals)
- Prevents the `networkidle` state from being reached
- Causes `goto(..., wait_until="networkidle")` to **hang forever**

### 🔍 Investigation

- A 900ms delay allowed the **main content to be visible**
- Capturing the network logs showed a file named:
    
    ```python
    loading-2c24ada4a968d3cf.js
    
    ```
    
- This confirmed a persistent loading mechanism tied to frontend rendering

---

## ✅ Solution: Wait for Loader to Disappear via Selector

### **Selector Identified**

The loader is rendered inside:

```html
<div class="logo-spin">...</div>

```

### **Fix in Code**

Replace `networkidle` with:

```python
page.goto("<https://digital.gov.eg>")
page.wait_for_selector(".logo-spin", state="detached")  # wait until loader is gone

```

---

## ✅ Outcome

- Page content loads fully
- Loader disappears
- DOM elements become available for scraping
- No hanging or false negatives

---

## 🚧 Stage 1: Extracting Categories and Active Service URLs

### 1. **Dynamic Content Loading via JavaScript**

- **Problem**: Service links for each category load only after clicking the category tab.
- **Diagnosis**: Initial HTML only contains one active category’s services. Others load dynamically via JavaScript on user interaction.
- **Solution**: Use **Playwright** to:
    - Load the `/categories/` page.
    - Identify and click each category button sequentially.
    - Wait for DOM update and scrape dynamically injected service links (`a[id^="categoryLink-"]`).
- **Outcome**: All active service links across categories are discovered and accessible.

---

### 2. **Excluding Inactive Services**

- **Problem**: Some displayed services lack URLs (e.g., "Coming Soon").
- **Diagnosis**: Inactive services don’t use `<a>` tags; they appear as `div.secCard.servLinkDim`.
- **Solution**:
    - Query specifically for `a[id^="categoryLink-"]` to fetch only linked (active) services.
    - Use `page.query_selector_all()` instead of `wait_for_selector()` to avoid timeout errors.
    - Skip categories with zero active links.
- **Outcome**: Only usable, live services are collected with zero script failures.

---

### 3. **Structured JSON Output**

- **Goal**: Preserve the relationship between categories and services.
- **Solution**:
    - Use `defaultdict(list)` to group services under their category.
    - Save results using `json.dump(..., ensure_ascii=False, indent=4)`.
- **Output File**: `services_by_category.json`
- **Outcome**: Readable, Arabic-supporting JSON ready for detail scraping.

---

## 🚧 Stage 2: Scraping Individual Service Details

### 4. **Avoiding Full Browser Overhead**

- **Problem**: Using Playwright to scrape each service page is slow and inefficient.
- **Diagnosis**: Service details are present in the initial HTML source, no JS rendering needed.
- **Solution**:
    - Use `requests` for fast HTML download.
    - Parse using `BeautifulSoup`.
- **Outcome**: Lightweight, high-speed detail scraper using minimal resources.

---

### 5. **Handling Accordion-Based Layouts**

- **Problem**: Service detail sections (description, terms, etc.) are inside accordion components with **non-distinctive classes**.
- **Diagnosis**: The headers (`<h2>`) of each accordion section use **unique Arabic titles**, e.g.:
    - "وصف الخدمة" (Description)
    - "شروط و أحكام الخدمة" (Terms)
    - "المستندات المطلوبة" (Documents)
    - "خدمات مشابهة" (Related Services)
- **Solution**:
    - Loop through all `div.MuiAccordion-root` sections.
    - Match `h2` header text to known section labels.
    - Map each section’s content via its label to a dictionary for clean access.
- **Outcome**: Accurate parsing despite shared classes by using semantic header text.

---

### 6. **Cleaning Terms & Documents as Lists**

- **Problem**: Terms and Documents are in multiple `<p>` tags, sometimes prefixed with .
- **Diagnosis**: Raw text extraction results in cluttered, hard-to-use blocks.
- **Solution**:
    - Extract each `<p>` tag’s text separately.
    - Strip whitespace and leading  or bullets.
    - Represent them as clean `List[str]`.
- **Outcome**: Usable, structured lists in final JSON.

---

### 7. **Interpreting “لا يوجد” as Empty List**

- **Problem**: Sections like Terms or Documents may contain only “لا يوجد” (None).
- **Diagnosis**: This placeholder appears in a single `<p>` element.
- **Solution**:
    - If the cleaned list equals `["لا يوجد"]`, convert it to `[]`.
    - Encapsulated into a reusable `extract_list_content()` helper function.
- **Outcome**: Accurate representation of "no data" fields.

---

### 8. **Progress Tracking with Clean Output**

- **Problem**: Printing errors clutters progress bars (e.g., with `tqdm`).
- **Solution**:
    - Wrap service scraping loop with `tqdm`.
    - Use `print(..., file=sys.stderr)` for errors to avoid interfering with progress display.
- **Outcome**: Clean, user-friendly progress tracking with unobtrusive error reporting.

---

### 9. **Clear Structure with Type Hinting**

- **Problem**: Hard to infer final output structure from raw dicts.
- **Solution**:
    - Define `TypedDict` structures (`ScrapedServiceData`, `RelatedService`) for output schema.
    - Add type hints for clarity and static analysis (`mypy`, IDE autocomplete).
- **Outcome**: Readable, maintainable code with safer development via type checking.

---

## ✅ Final Output

A unified `scraped_services_data.json` file containing:

```json
[
  {
    "category": "Category Name",
    "service_name": "Service Title",
    "service_url": "https://digital.gov.eg/services/.../",
    "description": "Full service description...",
    "terms": ["Term 1", "Term 2", "..."],
    "documents": ["Document 1", "..."],
    "related_services": [
      {"text": "Another service", "link": "https://..."},
      ...
    ]
  },
  ...
]

```