from enum import Enum


class JobLocation(str, Enum):
    """Work location type for a job posting."""

    ON_SITE = "on-site"
    HYBRID = "hybrid"
    REMOTE = "remote"
