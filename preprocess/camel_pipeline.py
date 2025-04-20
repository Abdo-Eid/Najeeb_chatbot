import re
from typing import List
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.normalize import normalize_unicode, normalize_alef_maksura_ar, normalize_alef_ar, normalize_teh_marbuta_ar
import numpy as np
from stopwordsallforms import STOPWORDS
from camel_tools.utils.dediac import dediac_ar
from sklearn.feature_extraction.text import TfidfVectorizer

def norm(text):
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

# Tokenization (and it Dediacritization )


def preprocess_text(text):
    '''text->tokens->cleaned_tokens->normalized_tokens'''
    text = re.sub(r'[^\w\s]', '', text)
    # Remove punctuations from each token
    tokens = simple_word_tokenize(text)



    # Stopword Removal and Filtering and normalization
    ar_stopwords = set(STOPWORDS.keys())

    return [norm(token) for token in tokens if token not in ar_stopwords and len(token) > 1]

def extract_keywords_tfidf(service_full_texts: List[str], top_n=2):
    """
    service_full_texts: List of strings (each string = full text of a service)
    top_n: Number of top keywords to extract for each service
    """
    if not service_full_texts:
        return []

    # If a single string is passed, convert it into a list with one item
    if isinstance(service_full_texts, str):
        service_full_texts = [service_full_texts]

    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(service_full_texts)
    feature_names = vectorizer.get_feature_names_out()

    # Extract top keywords for each document (service)
    keywords = []
    for doc_idx in range(tfidf_matrix.shape[0]):
        scores = tfidf_matrix[doc_idx].toarray().flatten()
        top_indices = np.argsort(scores)[-top_n:][::-1]
        top_keywords = [feature_names[idx] for idx in top_indices if scores[idx] > 0]
        keywords.append(top_keywords)

    return keywords

#
def enrich_services_with_texts(services_data):
    """
    Adds 'full_text' and 'short_text' fields to each service in the list.
    Includes 'Documents' in full_text only if it's not "لا يوجد".
    """
    for service in services_data:
        category = service.get("category", "")
        name = service.get("service_name", "")
        desc = service.get("description", "")
        terms = " ".join(service.get("terms", []))
        documents = service.get("Documents", "")

        # إذا المستندات مش "لا يوجد"، نضيفها للنص
        if documents.strip() != "لا يوجد":
            full_text = f"{category} {name} {desc} {terms} {documents}"
        else:
            full_text = f"{category} {name} {desc} {terms}"

        # نحفظ النصوص
        service["full_text"] = full_text.strip()
        service["short_text"] = f"{desc} {name} {category}".strip()

    return services_data


def extract_keywords_from_short_texts(services_data, top_n=2):
    """
    Trains TF-IDF on 'full_text' of all services,
    then extracts top N keywords from each service's 'short_text'.
    """
    # Step 1: Fit TF-IDF on all full_texts
    full_texts = [service["full_text"] for service in services_data]
    vectorizer = TfidfVectorizer()
    vectorizer.fit(full_texts)
    feature_names = vectorizer.get_feature_names_out()

    # Step 2: Extract keywords from each short_text
    for service in services_data:
        short_text = service["short_text"]
        tfidf_vector = vectorizer.transform([short_text])
        scores = tfidf_vector.toarray().flatten()

        # Get top N keyword indices
        top_indices = np.argsort(scores)[-top_n:][::-1]
        keywords = [feature_names[i] for i in top_indices if scores[i] > 0]

        service["keywords"] = keywords

    return services_data
