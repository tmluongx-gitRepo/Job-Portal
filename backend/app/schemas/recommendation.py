"""
Recommendation schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MatchFactorSchema(BaseModel):
    """Individual matching factor schema"""

    factor: str
    weight: float
    explanation: str
    score: int  # 0-100


class RecommendationBase(BaseModel):
    """Base recommendation schema"""

    job_seeker_id: str
    job_id: str
    match_percentage: int  # 0-100
    reasoning: str
    factors: list[MatchFactorSchema]
    ai_generated: bool = True


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation"""


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation"""

    viewed: bool | None = None
    dismissed: bool | None = None
    applied: bool | None = None


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response"""

    id: str
    viewed: bool = False
    dismissed: bool = False
    applied: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationWithDetails(RecommendationResponse):
    """Recommendation with embedded job and profile details"""

    job_title: str | None = None
    job_company: str | None = None
    job_location: str | None = None
    job_salary_min: int | None = None
    job_salary_max: int | None = None
    job_seeker_name: str | None = None
