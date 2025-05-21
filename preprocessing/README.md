# Preprocessing

This folder contains scripts and utilities for preprocessing Arabic service data for downstream NLP tasks such as keyword extraction and vectorization.

## Main Script

-   **preprocess.py**  
    Handles normalization, tokenization, stopword removal, and feature extraction for service data.
    -   Normalizes Arabic text (removes diacritics, standardizes characters)
    -   Tokenizes and removes stopwords
    -   Enriches each service with normalized text fields
    -   Extracts top keywords using TF-IDF
    -   Saves enriched data and vectorizer artifacts

## Usage

1. Place your raw scraped service data in the location specified by `SCRAPED_SERVICES_FILE` in your config.
2. Run the script:
    ```bash
    python preprocess.py
    ```
3. The script will output:
    - Enriched services JSON file
    - Pickled TF-IDF vectorizer
    - Pickled service matrix

## Requirements

-   [camel-tools](https://github.com/CAMeL-Lab/camel_tools)
-   scikit-learn
-   numpy

## Output Fields

Each service is enriched with:

-   `full_text`: Normalized concatenation of category, name, description, and terms.
-   `short_text`: Normalized concatenation of category, name, and description.
-   `keywords`: Top keywords extracted from the service.

## Customization

-   Adjust stopwords in `stopwordsallforms`.
-   Change the number of keywords via the `top_n` parameter in `extract_keywords`.
