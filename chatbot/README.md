```bash
pip install flask flask-cors

```

- make function that take query and 
    - if it greeting and bye use the rule based chatbot
    - if real query can the tf-idf model and get the top 1 response will git the index of that service, so i can get the data from it
    - if the response is so far from the nearest vector (similarity) say don't know

Here’s a clean and complete `README.md` file for your Flask API project:

### 🚀 How to Run the API (Windows)

#### 1. 📦 Install dependencies

In the project directory, open Command Prompt or PowerShell and run:

```bash
pip install -r requirements.txt
```

#### 2. ▶️ Start the Flask server

```bash
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5000
```

---

### 🔗 API Endpoint

#### `POST /chat`

**Request:**

* Content-Type: `application/json`
* JSON payload:

```json
{
  "message": "اهلا"
}
```

**Response:**

* JSON:

```json
{
  "response": "ازيك عامل اي"
}
```

---

### 🧪 Example Testing

#### ✅ Using curl:

```python
import requests

response = requests.post("http://127.0.0.1:5000/chat", json={"message": "السلام عليكم"})
print(response.json())
```

#### ✅ Using Postman:

* Method: `POST`
* URL: `http://127.0.0.1:5000/chat`
* Body → Raw → JSON:

```json
{
  "message": "باي"
}
```
