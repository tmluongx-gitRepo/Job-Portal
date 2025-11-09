"""
Job model for ChromaDB.

In ChromaDB, jobs are stored as documents with embeddings for semantic search.
Each job document contains the job description as document content and
job metadata (title, company, salary, etc.) as metadata fields.
"""
from datetime import datetime
from uuid import uuid4



class Job:
    """Job model for ChromaDB."""

    def __init__(
        self,
        title: str,
        company: str,
        location: str,
        description: str,
        job_type: str,
        requirements: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        is_active: bool = True,
        job_id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = job_id or str(uuid4())
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.requirements = requirements
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.job_type = job_type  # full-time, part-time, contract
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_document(self) -> str:
        """
        Convert job to a text document for ChromaDB embedding.
        This text will be embedded for semantic search.
        """
        parts = [
            f"Job Title: {self.title}",
            f"Company: {self.company}",
            f"Location: {self.location}",
            f"Type: {self.job_type}",
            f"Description: {self.description}",
        ]

        if self.requirements:
            parts.append(f"Requirements: {self.requirements}")

        if self.salary_min and self.salary_max:
            parts.append(f"Salary: ${self.salary_min:,} - ${self.salary_max:,}")

        return "\n\n".join(parts)

    def to_metadata(self) -> dict:
        """Convert job to metadata dictionary for ChromaDB storage."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description[:500],  # Truncate for metadata
            "requirements": self.requirements[:500] if self.requirements else None,
            "salary_min": str(self.salary_min) if self.salary_min else None,
            "salary_max": str(self.salary_max) if self.salary_max else None,
            "job_type": self.job_type,
            "is_active": str(self.is_active),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_metadata(cls, metadata: dict, full_description: str | None = None) -> "Job":
        """Create job from ChromaDB metadata."""
        return cls(
            job_id=metadata.get("id"),
            title=metadata["title"],
            company=metadata["company"],
            location=metadata["location"],
            description=full_description or metadata["description"],
            requirements=metadata.get("requirements"),
            salary_min=int(metadata["salary_min"]) if metadata.get("salary_min") else None,
            salary_max=int(metadata["salary_max"]) if metadata.get("salary_max") else None,
            job_type=metadata["job_type"],
            is_active=metadata.get("is_active", "True") == "True",
            created_at=datetime.fromisoformat(metadata["created_at"]) if "created_at" in metadata else None,
            updated_at=datetime.fromisoformat(metadata["updated_at"]) if "updated_at" in metadata else None,
        )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title={self.title}, company={self.company})>"
