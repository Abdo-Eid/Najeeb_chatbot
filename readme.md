# Najeeb Chatbot - Egypt Digital Portal

## ✨ Our Story

![Najeeb Logo](logo.png)
Najeeb was born out of a desire to simplify access to Egypt's Digital Portal services. Navigating government websites can be overwhelming, so we envisioned an intelligent assistant that could quickly answer user questions. By combining web scraping, data preprocessing, and a smart chatbot architecture, Najeeb provides a user-friendly way to get information about digital services in Egypt.

## 🎬 Demo

![Demo](Demo.gif)

---
## ✅ Summary

We have built a comprehensive pipeline that can be run any time. It can be customized for any website with small tweaks:

1.  **Scraping:** Retrieves updated data.
2.  **Preprocessing:** A simple but powerful process that resulted in a less than 1MB TF-IDF model and matrix for retrieval.
    -   [ ] TODO: Can be enhanced later by using a morphological analyzer for lemmatization (achievable using Camel-tools).
3.  **Chatbot:** A mix between rule-based and corpus/retrieval-based chatbots for better conversation and human interaction.
4.  **API Integration:** A simple API integration for the UI.
5.  **CLI Tool:** A CLI tool to handle the pipeline and server.

An intelligent assistant that answers your questions about Egypt's Digital Portal services using web scraping, data preprocessing, and a combination of rule-based and TF-IDF retrieval chatbot logic.

## 🚀 Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Abdo-Eid/Najeeb_chatbot
    cd Najeeb_chatbot
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

1.  **Configure `config.py`:**  
    Review and adjust the file paths and chatbot rules in `config.py` to match your environment and desired chatbot behavior.

## 🛠️ Running the Pipeline

The project includes a CLI tool (`manage.py`) to run different parts of the pipeline.

1.  **Scrape service URLs:**

    ```bash
    python manage.py scrape_url
    ```

    This command uses Playwright to extract all service URLs from the Egypt Digital Portal, grouped by category, and saves them to `data/services_by_category.json`.

2.  **Scrape service details:**

    ```bash
    python manage.py scrape_services
    ```

    This command uses `requests` and `BeautifulSoup` to scrape details for each service URL and saves the data to `data/scraped_services_data.json`.

3.  **Preprocess the data:**

    ```bash
    python manage.py preprocess
    ```

    This command normalizes Arabic text, removes stopwords, extracts keywords using TF-IDF, and saves the enriched data, vectorizer, and service matrix to the `data/` directory.

4.  **Run the complete pipeline:**

    ```bash
    python manage.py run_pipeline
    ```

    This command executes the scraping and preprocessing steps sequentially.

## 🤖 Running the Chatbot

1.  **Start the Flask API server:**

    ```bash
    python manage.py run_app
    ```

    This starts the Flask server, which serves the chatbot API and web UI. You can add `--debug` to enable debug mode.

    ```bash
    python manage.py run_app --debug
    ```

2.  **Access the web UI:**

    Open your web browser and go to `http://127.0.0.1:5000` to interact with the chatbot.

## 🔗 API Usage

The chatbot provides a simple API endpoint for sending messages and receiving responses.

### `POST /chat`

**Request:**

-   Content-Type: `application/json`
-   Example request:

```json
{
    "message": "ما هي خدمات المرور؟"
}
```

**Response:**

```json
{
    "response": {
        "type": "tfidf",
        "data": {
            "category": "خدمات المرور",
            "service_name": "استخراج شهادة بيانات لرخصة قيادة",
            "service_url": "https://digital.gov.eg/services/654a2c9f18e999a945badc97",
            "description": "تتيح لك هذه الخدمة استخراج شهادة بيانات لرخصة القيادة الخاصة بك.",
            "terms": ["رخصة القيادة", "شهادة بيانات", "المرور"],
            "keywords": ["شهادة", "بيانات", "رخصة", "قيادة"]
        }
    }
}
```

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes.
4.  Test your changes thoroughly.
5.  Submit a pull request with a clear description of your changes.

