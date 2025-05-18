import json
import os
import pickle
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from camel_pipeline import norm
import random

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "preprocess"))

# Load TF-IDF vectorizer
with open(os.path.join(BASE_DIR, "tfidf_vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)

# Load services data
with open(os.path.join(BASE_DIR, "services_with_keywords.json"), "r", encoding="utf-8") as f:
    services_data = json.load(f)

# Load TF-IDF matrix of service full_texts
service_tfidf_matrix = sparse.load_npz(os.path.join(BASE_DIR, "service_tfidf_matrix.npz"))

# Rule-based greetings/farewells
RESPONSE_RULES = {
    # --- Greetings ---
    "السلام عليكم": ["وعليكم السلام", "وعليكم السلام ورحمة الله وبركاته"],
    "سلام عليكم": ["وعليكم السلام", "وعليكم السلام ورحمة الله وبركاته"], # Common variation
    "اهلا": ["أهلاً بك!", "يا هلا!", "مرحباً بك، كيف يمكنني مساعدتك اليوم؟", "نورتنا"],
    "أهلا": ["أهلاً بك!", "يا هلا!", "مرحباً بك، كيف يمكنني مساعدتك اليوم؟", "نورتنا"], # With Alef Madda
    "مرحبا": ["أهلاً وسهلاً", "مرحباً بك!", "يا هلا فيك", "نورت"],
    "صباح الخير": ["صباح النور", "صباح الفل", "صباح الورد والياسمين"],
    "مساء الخير": ["مساء النور", "مساء الفل", "مساء الورد"],
    "نهارك سعيد": ["ونهارك أسعد بإذن الله", "يومك سعيد أيضاً"],
    "يا هلا": ["يا مرحب", "أهلين فيك"],
    "أهلا وسهلا": ["أهلاً بك", "يا مرحبا بك"], # As a key as well

    # --- Farewells ---
    "باي": ["مع السلامة", "في أمان الله", "إلى اللقاء", "نشوفك على خير"],
    "مع السلامة": ["في رعاية الله", "الله يسلمك، مع السلامة", "إلى اللقاء قريباً"],
    "سلام": ["مع السلامة", "في حفظ الرحمن"], # Common short farewell
    "اشوفك بعدين": ["إن شاء الله، مع السلامة", "في انتظارك"],
    "الى اللقاء": ["إلى لقاء قريب بإذن الله", "مع السلامة"],
    "في امان الله": ["في حفظه ورعايته", "الله معك"], # As a key

    # --- Pleasantries & Thanks ---
    "شكرا": ["على الرحب والسعة", "العفو", "لا شكر على واجب", "بكل سرور"],
    "شكرا جزيلا": ["العفو، هذا واجبي", "سعدت بمساعدتك"],
    "تسلم": ["الله يسلمك", "العفو"],
    "متشكر": ["العفو", "الشكر لله"],
    "الله يخليك": ["ويخليك يا رب", "تسلم"], # Can be a response to thanks
    "العفو": ["تسلم", "شكراً لك"], # If user says "العفو" first

    # --- Common Questions/Interactions ---
    "كيف حالك": ["الحمد لله بخير، شكراً لسؤالك. كيف يمكنني مساعدتك؟", "بخير، أتمنى أن تكون كذلك. تفضل."],
    "ازيك": ["تمام الحمد لله، وأنت؟ كيف أقدر أساعدك؟", "كويس، شكراً. أؤمرني؟"],
    "عامل ايه": ["كله تمام الحمد لله. أقدر أساعدك بإيه؟", "بخير، شكراً لك. تفضل بسؤالك."],
    "اخبارك ايه": ["الحمد لله كله تمام. كيف يمكنني خدمتك؟", "أخباري جيدة، شكراً. تفضل."],
    "تمام": ["الحمد لله", "عظيم!", "جيد جداً"], # Acknowledging user's "تمام"
    "ماشي": ["تمام", "حسناً", "بالتأكيد"],
    "اوكي": ["حسناً", "تمام", "موافق"],
    "ok": ["حسناً", "تمام", "موافق"], # Common English variation
    "حسنا": ["تمام", "بالتأكيد"],
    "لو سمحت": ["تفضل، أؤمرني", "أكيد، تحت أمرك"],
    "من فضلك": ["تفضل بسؤالك", "أنا في الخدمة"],
    "ممكن سؤال": ["بالتأكيد، تفضل بسؤالك.", "اسأل ما تشاء، أنا هنا للمساعدة."],
    "عندي سؤال": ["تفضل، كلي آذان صاغية.", "اطرح سؤالك، سأحاول المساعدة قدر الإمكان."],

    # --- About the Bot (Optional but good for rule-based) ---
    "مين انت": ["أنا نجيب، مساعدك الرقمي من بوابة مصر الرقمية.", "اسمي نجيب، كيف أقدر أساعدك؟"],
    "انت مين": ["أنا نجيب، مساعدك الرقمي.", "معك نجيب، للمساعدة في خدمات بوابة مصر الرقمية."],
    "اسمك ايه": ["اسمي نجيب.", "أنا نجيب، مساعدك الافتراضي."],
    "بتعمل ايه": ["أنا هنا لمساعدتك في العثور على معلومات وخدمات بوابة مصر الرقمية.", "وظيفتي هي إرشادك لخدمات الحكومة الرقمية."],
    "وظيفتك ايه": ["أساعدك في استكشاف خدمات بوابة مصر الرقمية والإجابة على استفساراتك المتعلقة بها.", "أنا دليلك لخدمات مصر الرقمية."],
    "ما هي خدماتك": ["يمكنني مساعدتك في البحث عن خدمات حكومية، معرفة شروطها، والوصول إليها عبر بوابة مصر الرقمية.", "أقدم معلومات حول الخدمات المتاحة على بوابة مصر الرقمية."],

    # --- Simple confirmations/negations (can be useful) ---
    "ايوه": ["تمام", "حسناً"],
    "نعم": ["تمام", "بالتأكيد"],
    "لا": ["حسناً", "مفهوم"],
    "صح": ["بالتأكيد", "صحيح"],
    "مضبوط": ["تماماً", "بالفعل"],
}


DEFAULT_RESPONSE = "عذراً، لم أفهم سؤالك."

def get_rule_response(user_input):
    normalized = norm(user_input)
    response = RESPONSE_RULES.get(normalized)
    if isinstance(response, list):
        return random.choice(response)
    elif isinstance(response, str):
        return response
    else:
        return None

def get_tfidf_response(user_input, similarity_threshold=0.3):
    normalized = norm(user_input)
    query_vec = vectorizer.transform([normalized])
    similarities = cosine_similarity(query_vec, service_tfidf_matrix).flatten()
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]

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

def get_bot_response(user_input):
    # 1) Try rule-based first (greeting/bye)
    rule_response = get_rule_response(user_input)
    if rule_response:
        return {"type": "rule", "response": rule_response}
    
    # 2) Try TF-IDF similarity matching
    tfidf_response = get_tfidf_response(user_input)
    if tfidf_response:
        return {"type": "tfidf", "data": tfidf_response}
    
    # 3) Default fallback
    return {"type": "default", "response": DEFAULT_RESPONSE}
