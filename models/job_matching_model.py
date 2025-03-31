from pydantic import BaseModel
from typing import List

class JobMatchingResponse(BaseModel):
    title: str
    company: str
    location: str
    matching_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendation: str
    url: str