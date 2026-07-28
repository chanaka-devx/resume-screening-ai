from enum import Enum


class JobStatus(str, Enum):
    """
    Valid lifecycle states for a JobPosting.

    Allowed transitions:
        DRAFT → PUBLISHED
        PUBLISHED → CLOSED
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    DELETED = "deleted"
