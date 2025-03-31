from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import string

# Download NLTK data (run once)
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """
    Preprocess text by:
    - Converting to lowercase
    - Removing punctuation
    - Removing stopwords
    - Lemmatizing words
    """
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove stopwords and lemmatize
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    print(f"Preprocessed text: {words}")  # Debug statement
    return ' '.join(words)

def calculate_ats_score(resume_text, job_description):
    """
    Calculate ATS score using TF-IDF and cosine similarity.
    """
    # Preprocess resume and job description
    resume_text = preprocess_text(resume_text)
    job_description = preprocess_text(job_description)

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])

    # Debug: Print TF-IDF vectors
    print("TF-IDF Matrix:")
    print(tfidf_matrix.toarray())

    # Calculate cosine similarity between resume and job description
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    ats_score = similarity[0][0] * 100  # Convert to percentage

    return round(ats_score, 2)