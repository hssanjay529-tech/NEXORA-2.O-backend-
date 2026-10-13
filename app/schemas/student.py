import uuid
from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


# Enrolment
class CourseRegisterRequest(BaseModel):
    offering_ids: Optional[List[uuid.UUID]] = None
    course_offering_id: Optional[uuid.UUID] = None
    course_id: Optional[uuid.UUID] = None


# Assignment Submission
class AssignmentSubmitRequest(BaseModel):
    file_id: Optional[uuid.UUID] = None
    answers: Optional[Dict[str, Any]] = None


# Fee Payments
class FeePaymentRequest(BaseModel):
    fee_record_id: uuid.UUID
    amount: Decimal
    method: str = "CARD"  # CARD, UPI, NET_BANKING, etc.
    gateway_ref: Optional[str] = None


# Exam Registration
class ExamRegisterRequest(BaseModel):
    exam_id: uuid.UUID


# Grievances
class GrievanceCreate(BaseModel):
    category: str  # ACADEMIC, FINANCE, FACILITY, EXAMINATION, HARASSMENT, OTHER
    title: str
    description: str
    priority: Optional[str] = "MEDIUM"


class GrievanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: str
    title: str
    description: str
    status: str
    priority: str
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


# Document Requests
class DocumentRequestCreate(BaseModel):
    doc_type: str  # BONAFIDE, TRANSCRIPT, GRADE_CARD, TRANSFER_CERTIFICATE, COURSE_COMPLETION, OTHER
    remarks: Optional[str] = None


class DocumentRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    doc_type: str
    status: str
    verification_code: str
    remarks: Optional[str] = None
    file_id: Optional[uuid.UUID] = None
    requested_at: datetime


# Direct Messaging
class DirectMessageSendRequest(BaseModel):
    recipient_user_id: uuid.UUID
    body: str
    file_id: Optional[uuid.UUID] = None
