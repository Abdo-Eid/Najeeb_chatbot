import json
import os
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random
from preprocessing.preprocess import norm
from config import RESPONSE_RULES, DEFAULT_RESPONSE, VECTORIZER_FILE, DEPLOYMENT_SERVICES_FILE, SERVICES_MATRIX_FILE

# Load TF-IDF vectorizer
with open(VECTORIZER_FILE, "rb") as f:
    vectorizer = pickle.load(f)

# Load services data
with open(os.path.join(DEPLOYMENT_SERVICES_FILE), "r", encoding="utf-8") as f:
    services_data = json.load(f)

# Load TF-IDF matrix (pickle file)
with open(SERVICES_MATRIX_FILE, "rb") as f:
    service_tfidf_matrix = pickle.load(f)

def get_rule_response(user_input):
    normalized = norm(user_input)
    response = RESPONSE_RULES.get(normalized)
    if isinstance(response, list):
        return random.choice(response)
    elif isinstance(response, str):
        return response
    else:
        return None

def get_tfidf_response(user_input, similarity_threshold=0.3, debug=False):
    query_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(query_vec, service_tfidf_matrix).flatten()
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]

    if debug:
        print(f"[DEBUG] Best index: {best_idx}, Best score: {best_score}")

    if best_score < similarity_threshold:
        return None

    service = services_data[best_idx]
    return {
        "category": service.get("category", ""),
        "service_name": service.get("service_name", ""),
        "service_url": service.get("service_url", ""),
        "description": service.get("description", ""),
        "terms": service.get("terms", []),
        "keywords": service.get("keywords", []),
    }

def get_bot_response(user_input, debug = False):
    # 1) Try rule-based first (greeting/bye)
    rule_response = get_rule_response(user_input)
    if rule_response:
        return {"type": "rule", "response": rule_response}
    
    # 2) Try TF-IDF similarity matching
    tfidf_response = get_tfidf_response(user_input, debug=debug)
    if tfidf_response:
        return {"type": "tfidf", "data": tfidf_response}
    
    # 3) Default fallback
    return {"type": "default", "response": DEFAULT_RESPONSE}
