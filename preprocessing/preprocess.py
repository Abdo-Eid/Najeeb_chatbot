from collections import defaultdict
import re
from typing import List
import numpy as np
from .stopwordsallforms import STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from scraping.scraper import ScrapedServiceData

class EnrichedServiceData(ScrapedServiceData, total=False):
    full_text: str
    short_text: str


# ============================= removing camel-tool from production code for it's big dependancy =======================

import re

def dediac_ar(text: str) -> str:
    """
    Removes Arabic diacritics from the text.
    """
    arabic_diacritics = re.compile(r'[\u0610-\u061A\u064B-\u065F\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]')
    return re.sub(arabic_diacritics, '', text)

def normalize_unicode(text: str) -> str:
    """
    Normalizes common Unicode variations (basic NFC normalization).
    """
    import unicodedata
    return unicodedata.normalize('NFC', text)

def normalize_alef_ar(text: str) -> str:
    """
    Converts أ, إ, and آ to ا.
    """
    return re.sub(r'[إأآ]', 'ا', text)

def normalize_alef_maksura_ar(text: str) -> str:
    """
    Converts ى to ي.
    """
    return text.replace('ى', 'ي')

def normalize_teh_marbuta_ar(text: str) -> str:
    """
    Converts ة to ه.
    """
    return text.replace('ة', 'ه')

def simple_word_tokenize(text):
    return re.findall(r'\b\w+\b', text)

def norm(text: str) -> str:
    """
    Normalizes Arabic text by:
    1. Converting أ/إ/آ to ا [[3]]
    2. Normalizing ي to ى where appropriate [[3]]
    3. Handling common Unicode character variations [[9]]
    4. Removing diacritics (optional, requires separate function)
    """
    # Step 1: Basic Unicode normalization
    
    normalized_text = normalize_unicode(text)
    normalized_text = dediac_ar(normalized_text)
    
    # Step 2: Apply specific character normalizations
    normalized_text = normalize_alef_ar(normalized_text)    # Convert إأآ to ا
    normalized_text = normalize_alef_maksura_ar(normalized_text)  # Normalize ي/ى
    normalized_text = normalize_teh_marbuta_ar(normalized_text)   # Normalize ة to ه
    
    return normalized_text

def preprocess_text(text: str) -> List[str]:
    """
    - Remove punctuation
    - Tokenize (CamelTools)
    - Remove stopwords
    - Normalize each token
    """
    text = re.sub(r'[^\w\s]', '', text)
    tokens = simple_word_tokenize(text)
    return [norm(token) for token in tokens if len(token) > 1]

def category_level_full_texts(services_data: List[EnrichedServiceData]) -> List[str]:
    """
    Groups services by category and returns, for each service, the concatenated full_texts of its category.
    """
    # Group full_texts by category
    category_to_texts = defaultdict(list)
    for service in services_data:
        category = service.get("category", "")
        category_to_texts[category].append(service["full_text"])
    # Create a mapping: category -> concatenated full_text
    category_to_bigtext = {cat: " ".join(texts) for cat, texts in category_to_texts.items()}
    # For each service, assign the bigtext of its category
    category_full_texts = [category_to_bigtext[service.get("category", "")] for service in services_data]
    return category_full_texts

def enrich_services_with_texts(services_data: List[ScrapedServiceData]) -> List[EnrichedServiceData]:
    """
    For each service, add normalized 'full_text' and 'short_text' fields.
    """
    for service in services_data:
        # Get each relevant field, defaulting to empty string if missing
        category = service.get("category", "")
        name = service.get("service_name", "")
        desc = service.get("description", "")
        # Join terms list into a single string
        terms = " ".join(service.get("terms", []))
        documents = " ".join(service.get("terms", []))
        # Concatenate all fields for full_text
        full_text = f"{category} {name} {desc} {terms} {documents}"
        service["full_text"] = norm(full_text)
        # Concatenate description, name, and category for short_text
        service["short_text"] = norm(f"{category} {name} {desc}")
    return services_data

def extract_keywords(
    services_data: List[EnrichedServiceData], top_n: int = 4
) -> tuple[list[EnrichedServiceData], TfidfVectorizer, np.ndarray]:
    """
    - Train TF-IDF on all full_texts (preprocessed).
    - For each service, extract top N keywords from its short_text.
    - Save keywords in service['keywords'].
    """
    normalized_stopwords = [norm(word) for word in STOPWORDS.keys()]

    # Fit vectorizer on all full_texts (list of strings)
    category_full_texts = category_level_full_texts(services_data)
    vectorizer = TfidfVectorizer(stop_words=normalized_stopwords, tokenizer=preprocess_text, token_pattern=None)
    vectorizer.fit(category_full_texts)
    feature_names = vectorizer.get_feature_names_out()

    # Transform all short_texts (list of strings)
    short_texts = [service["short_text"] for service in services_data]
    services_matrix = vectorizer.transform(short_texts)  # shape: (n_services, n_features)

    for idx, service in enumerate(services_data):
        scores = services_matrix[idx].toarray().flatten()
        top_indices = np.argsort(scores)[-top_n:][::-1]
        keywords = [feature_names[i] for i in top_indices if scores[i] > 0]
        service["keywords"] = keywords

    return services_data, vectorizer, services_matrix

def preprocess():
    import json
    import pickle
    from config import SCRAPED_SERVICES_FILE, ENRICHED_SERVICES_FILE, VECTORIZER_FILE, SERVICES_MATRIX_FILE, DEPLOYMENT_SERVICES_FILE

    print("Loading services data...")
    # Load services data
    with open(SCRAPED_SERVICES_FILE, "r", encoding="utf-8") as f:
        services_data = json.load(f)

    # Enrich and extract keywords
    print("Enriching services with normalized full_text and short_text fields...")
    enriched_services = enrich_services_with_texts(services_data)
    
    print("Extracting keywords using TF-IDF...")
    enriched_services, vectorizer, services_matrix = extract_keywords(enriched_services, top_n=4)

    print("Saving enriched services data...")
    # Save enriched services data
    with open(ENRICHED_SERVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_services, f, ensure_ascii=False, indent=2)

    print("Saving deployment service data (original scraped data + keywords)...")
    # add the extracted keywords from the enriched data to the original data.
    for orig, enriched in zip(services_data, enriched_services):
        orig["keywords"] = enriched.get("keywords", [])

    with open(DEPLOYMENT_SERVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(services_data, f, ensure_ascii=False, indent=2)

    # Save vectorizer and matrix
    with open(VECTORIZER_FILE, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(SERVICES_MATRIX_FILE, "wb") as f:
        pickle.dump(services_matrix, f)

    print("Preprocessing and saving completed.")

if __name__ == "__main__":
    preprocess()
