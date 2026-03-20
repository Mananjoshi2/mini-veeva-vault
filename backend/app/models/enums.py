from enum import StrEnum


class UserRole(StrEnum):
    RESEARCHER = "Researcher"
    REVIEWER = "Reviewer"
    ADMIN = "Admin"


class DocumentStatus(StrEnum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"

