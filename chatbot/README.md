# Najeeb Chatbot - Egypt Digital Portal

An intelligent assistant that answers your questions about Egypt's Digital Portal services using Flask and TF-IDF.

---

## 🚀 How to Run (Windows)

### 1. Install requirements

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install flask flask-cors
```

### 2. Start the server

```bash
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5000
```

---

## 🔗 API Endpoint

### `POST /chat`

**Request:**

-   Content-Type: `application/json`
-   Example request:

```json
{
    "message": "hello"
}
```

**Response:**

-   Example response:

```json
{
    "response": {
        "type": "rule",
        "response": "How are you?"
    }
}
```

---

## 🧪 Example Testing

### Using Python (requests):

```python
import requests

response = requests.post("http://127.0.0.1:5000/chat", json={"message": "hello"})
print(response.json())
```

### Using Postman:

-   Method: `POST`
-   URL: `http://127.0.0.1:5000/chat`
-   Body → Raw → JSON:

```json
{
    "message": "bye"
}
```

---

## 🧠 How does the chatbot work?

-   If the message is a greeting or farewell: uses rule-based responses.
-   If it's a real query: uses the TF-IDF model and returns the best matching service.
-   If no close answer is found (low similarity): replies that it doesn't know the answer.
