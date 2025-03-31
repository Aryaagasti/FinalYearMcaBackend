from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.keyword_extractor import preprocess_text

def calculate_ats_score(resume_text, job_description):
    """
    Calculate ATS score using TF-IDF and cosine similarity.
    """
    # Preprocess text
    resume_text = preprocess_text(resume_text)
    job_description = preprocess_text(job_description)

    if not resume_text or not job_description:
        print("One of the inputs is empty after preprocessing.")
        return 0.0

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(max_features=500, stop_words="english")  # Limit feature size
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])

    # Compute cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    ats_score = similarity[0][0] * 100  # Convert similarity to percentage

    print(f"ATS Score: {ats_score:.2f}%")
    return round(ats_score, 2)
