## 📘 Scraping `digital.gov.eg`: Problem-Solution Sequence

---

### 1. ❌ Initial Approach: `requests_html` Fails to Render Content

#### **Code Used**
```python
from requests_html import HTMLSession

session = HTMLSession()
url = "https://digital.gov.eg/"
response = session.get(url)
response.html.render()
item = response.html.xpath("/html/body/main/div[1]/div/div/h1", first=True)
```

#### **Issue**
- `.render()` uses Pyppeteer internally to load JS content
- Pyppeteer Chromium **failed to download** due to a broken URL:
  ```
  OSError: Chromium downloadable not found at ...
  ```
- No maintained fork of `requests_html` is available
- Even if Chromium had been available, rendering was unreliable for modern JS frameworks (like React)

---

### 2. ✅ Migration to Playwright

#### Initial Code

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://digital.gov.eg", wait_until="load")
    element = page.locator("//html/body/main/div[1]/div/div/h1")
    print(element.nth(0).inner_text())
```

#### **New Problem**
- Using `wait_until="load"` finishes when **basic HTML is loaded**
- However, the **real content is rendered by JS after the loader disappears**
- Result: `element.nth(0)` returns nothing or raises an error
- The main element was **not found** even though the page was technically loaded

---

## 3. 🐛 Problem: Playwright Hangs on `networkidle` Due to Persistent Loader

### 📌 Context
While scraping `https://digital.gov.eg/` using Playwright, the script would hang indefinitely when using:

```python
page.goto("https://digital.gov.eg", wait_until="networkidle")
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
page.goto("https://digital.gov.eg")
page.wait_for_selector(".logo-spin", state="detached")  # wait until loader is gone
```

---

## ✅ Outcome

- Page content loads fully
- Loader disappears
- DOM elements become available for scraping
- No hanging or false negatives


