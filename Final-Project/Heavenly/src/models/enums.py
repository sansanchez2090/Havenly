from enum import Enum

class UserStatus(str, Enum):
    BANNED = "BANNED"
    VERIFIED = "VERIFIED"

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    REVIEWED = "REVIEWED"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"

class ReviewStatus(str, Enum):
    REPORTED = "REPORTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    HIDDEN = "HIDDEN"