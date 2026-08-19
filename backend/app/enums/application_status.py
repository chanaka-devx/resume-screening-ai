from enum import Enum


class ApplicationStatus(str, Enum):
    """
    Application status during recruitment pipeline.
    """
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    REJECTED = "rejected"
