from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.keyword_extractor import preprocess_text
import math

def calculate_ats_score(resume_text, job_description):
    """
    Calculate ATS score combining both keyword matching and structural analysis
    following the same logic as the JavaScript version but with Python implementation.
    """
    if not resume_text or not job_description or not isinstance(resume_text, str) or not isinstance(job_description, str):
        return 0
    
    try:
        # Preprocess texts
        processed_resume = preprocess_text(resume_text)
        processed_jd = preprocess_text(job_description)
        
        if not processed_resume or not processed_jd:
            return 0

        # 1. Keyword matching score (70% of total)
        # Using TF-IDF and cosine similarity for keyword matching
        vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([processed_resume, processed_jd])
        keyword_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        keyword_score = min(70, keyword_similarity * 70)  # 70 points max for keywords

        # 2. Resume length score (10% of total)
        word_count = len(processed_resume.split())
        if word_count > 500:
            length_score = 10
        elif word_count > 300:
            length_score = 7
        elif word_count > 100:
            length_score = 5
        else:
            length_score = 0

        # 3. Section presence score (20% of total)
        sections = ['experience', 'education', 'skills', 'projects']
        section_count = sum(1 for section in sections if section in processed_resume.lower())
        section_score = section_count * 5  # 5 points per section

        # Calculate total score
        total_score = keyword_score + length_score + section_score
        return min(100, math.ceil(total_score))  # Cap at 100 and round up

    except Exception as e:
        print(f'ATS score calculation error: {e}')
        return 0  # Return minimum score on error
