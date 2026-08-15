from enum import Enum


class RecruiterRole(str, Enum):
    """
    Access roles for a Recruiter account.

    RECRUITER  – default, standard hiring access
    ADMIN      – elevated access for platform management
    """

    RECRUITER = "recruiter"
    ADMIN = "admin"
