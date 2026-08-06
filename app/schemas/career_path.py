from datetime import date
from typing import Optional

from pydantic import BaseModel


class CareerProfileCreate(BaseModel):
    career_goal: str
    full_name: str
    date_of_birth: date
    education_stage: str


class CareerProfileResponse(BaseModel):
    id: str
    user_id: str
    career_goal: str
    full_name: str
    date_of_birth: date
    education_stage: str

    class Config:
        from_attributes = True


class CareerRoadmapResponse(BaseModel):
    phase_number: int
    phase_title: str
    duration: str
    description: str

    class Config:
        from_attributes = True

class CareerPathRequest(BaseModel):
    goal: str
    name: str
    age: int
    education: str
class CareerPathResponse(BaseModel):
    career_goal: str
    career_persona: str
    confidence_score: int
    current_stage: str
    recommended_stream: str
    primary_skill: str
    career_overview: str
    next_step: str
    target_exams: list[str]
    roadmap: list[dict]    
class CareerReportResponse(BaseModel):
    id: str
    career_persona: str
    confidence_score: int
    recommended_stream: str
    primary_skill: str
    career_overview: str
    next_step: str
    target_exams: Optional[str] = None
    roadmap: list[CareerRoadmapResponse] = []

    class Config:
        from_attributes = True