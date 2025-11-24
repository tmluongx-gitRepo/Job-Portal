"""
Resume schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeUploadResponse(BaseModel):
    """Schema for resume upload response"""

    id: str
    job_seeker_id: str
    original_filename: str
    dropbox_path: str
    uploaded_at: datetime
    content_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeMetadataResponse(BaseModel):
    """Schema for resume metadata response (no file download)"""

    id: str
    original_filename: str
    uploaded_at: datetime
    content_type: str

    model_config = ConfigDict(from_attributes=True)
