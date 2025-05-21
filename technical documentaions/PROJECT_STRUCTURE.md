# 📁 Project Structure & Architecture Overview

This document explains how the Najeeb Chatbot project is organized, the rationale behind its structure, and key architectural choices.

---

## 🗂️ Directory Layout

```
Najeeb_chatbot/
│
├── config.py                # Central configuration (paths, rules, constants)
├── manage.py                # CLI entry point for running pipeline steps
│
├── data/                    # All intermediate and output data files
│   ├── services_by_category.json
│   ├── scraped_services_data.json
│   ├── enriched_services_data.json
│   ├── deployment_services.json
│   ├── vectorizer.pkl
│   └── services_matrix.pkl
│
├── scraping/                # Web scraping logic
│   ├── get_services_urls.py     # Scrape all service URLs by category (Playwright)
│   ├── scraper.py               # Scrape service details (requests + BeautifulSoup)
│   └── readme.md
│
├── preprocessing/           # Data cleaning, normalization, feature extraction
│   ├── preprocess.py            # Main preprocessing script (TF-IDF, keywords, etc.)
│   ├── stopwordsallforms.py     # Arabic stopwords list
│   └── README.md
│
├── chatbot/                 # Chatbot logic and UI
│   ├── app.py                   # Flask API server
│   ├── bot.py                   # Rule-based & TF-IDF retrieval logic
│   ├── index.html               # Web UI (static)
│   └── README.md
│
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata and dependencies
└── README.md                # High-level project overview
```

---

## 🛠️ Step-by-Step Pipeline

1. **Scraping**

    - `scraping/get_services_urls.py`: Uses Playwright to extract all service URLs grouped by category.
    - `scraping/scraper.py`: Uses requests + BeautifulSoup to scrape details for each service.
    - Output: `data/services_by_category.json`, `data/scraped_services_data.json`

2. **Preprocessing**

    - `preprocessing/preprocess.py`: Normalizes Arabic text, removes stopwords, extracts keywords with TF-IDF, and saves vectorizer/matrix.
    - Output: `data/enriched_services_data.json`, `data/vectorizer.pkl`, `data/services_matrix.pkl`, `data/deployment_services.json`

3. **Chatbot**

    - `chatbot/bot.py`: Combines rule-based responses (greetings, farewells, etc.) with TF-IDF retrieval for service queries.
    - `chatbot/app.py`: Flask API serving the chatbot.
    - `chatbot/index.html`: Simple web UI for user interaction.

4. **Management**
    - `manage.py`: CLI tool to run scraping, preprocessing, etc. (`python manage.py scrape_url`, `scrape_services`, `preprocess`...)

---

## ⚙️ Central Configuration

-   **`config.py`**: All file paths, constants, and rule-based responses are defined here.
    -   Ensures all scripts use consistent paths (e.g., for data files, models).
    -   Contains chatbot rules and default responses.
    -   Sets up `BASE_DIR` and adds it to `sys.path` for reliable imports across modules.

---

## 🧩 Import Path Handling

-   At the top of `config.py` and `manage.py`, the project root (`BASE_DIR`) is added to `sys.path`.
    -   This allows all modules to use absolute imports (e.g., `from scraping.scraper import ...`) regardless of the working directory.
    -   Prevents import errors and keeps the codebase modular.

---

## 📦 Data Flow

-   All intermediate and output files are stored in the `data/` directory, as defined in `config.py`.
-   Each pipeline step reads from and writes to these files, enabling easy reruns and debugging.

---

## 📝 Customization

-   To adapt the pipeline to a new website, only the scraping scripts typically need adjustment.
-   All other steps (preprocessing, chatbot logic) are data-driven and reusable.

---

## ✅ Summary

-   **Modular**: Each step is isolated in its own folder/script.
-   **Configurable**: All paths and rules are centralized.
-   **Reproducible**: Data files are versioned and stored in one place.
-   **Extensible**: Easy to add new preprocessing, chatbot, or UI features.
