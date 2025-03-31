import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Ensure necessary NLTK data is downloaded
nltk.download("stopwords")
nltk.download("wordnet")

# Initialize NLP tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def preprocess_text(text):
    """
    Preprocess text by:
    - Converting to lowercase
    - Removing punctuation
    - Removing stopwords
    - Lemmatizing words
    """
    if not text or len(text.strip()) == 0:
        return ""  # Handle empty text gracefully

    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    words = text.split()
    processed_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]

    return " ".join(processed_words)

def extract_keywords(text, top_n=10):
    """
    Extracts the most common keywords from the text after preprocessing.
    """
    processed_text = preprocess_text(text)
    words = processed_text.split()
    word_counts = Counter(words)
    return [word for word, _ in word_counts.most_common(top_n)]
