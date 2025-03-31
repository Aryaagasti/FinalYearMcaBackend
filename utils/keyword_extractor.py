# utils/keyword_extractor.py
from sklearn.feature_extraction.text import CountVectorizer

def extract_keywords(text, top_n=10):
    vectorizer = CountVectorizer(stop_words='english')
    word_count_matrix = vectorizer.fit_transform([text])
    word_counts = word_count_matrix.sum(axis=0)
    word_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    word_freq = sorted(word_freq, key=lambda x: x[1], reverse=True)
    return [word for word, freq in word_freq[:top_n]]
