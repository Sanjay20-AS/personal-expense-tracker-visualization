from src.utils import DEFAULT_CATEGORIES

KEYWORDS = {
    "Food": ["swiggy", "zomato", "restaurant", "lunch", "dinner", "breakfast", "grocery", "groceries", "snack", "cafe"],
    "Transportation": ["uber", "ola", "bus", "train", "metro", "fuel", "petrol", "cab", "auto", "parking"],
    "Shopping": ["amazon", "flipkart", "clothes", "shopping", "mall"],
    "Bills": ["electricity", "internet", "mobile", "water bill", "recharge", "bill"],
    "Education": ["course", "coursera", "book", "stationery", "tuition", "college"],
    "Health": ["pharmacy", "medicine", "hospital", "doctor", "medical", "apollo"],
    "Entertainment": ["movie", "netflix", "spotify", "game", "concert", "entertainment"],
    "Housing": ["rent", "maintenance", "housing"],
    "Personal Care": ["salon", "grooming", "personal care", "haircut"],
}

def categorize(description: str, fallback="Other") -> str:
    text = str(description or "").strip().lower()
    for category, words in KEYWORDS.items():
        if any(word in text for word in words):
            return category
    return fallback if fallback in DEFAULT_CATEGORIES else "Other"
