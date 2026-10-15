import uuid
from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, EmailStr, ConfigDict


# User Management
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str  # 'ADMIN', 'FACULTY', 'STUDENT'
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    # Student specific
    programme_id: Optional[uuid.UUID] = None
    roll_no: Optional[str] = None
    admission_year: Optional[int] = None
    current_term_no: Optional[int] = 1
    # Faculty specific
    department_id: Optional[uuid.UUID] = None
    employee_no: Optional[str] = None
    designation: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    status: Optional[str] = None  # 'ACTIVE', 'INACTIVE', 'ARCHIVED'
    # Profile update
    designation: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    current_term_no: Optional[int] = None


class FacultyProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    department_id: uuid.UUID
    employee_no: str
    designation: str


class StudentProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    programme_id: uuid.UUID
    roll_no: str
    admission_year: int
    current_term_no: int
    status: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: str
    avatar_url: Optional[str] = None
    status: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    faculty_profile: Optional[FacultyProfileOut] = None
    student_profile: Optional[StudentProfileOut] = None


# Academic Calendar & Terms
class AcademicYearCreate(BaseModel):
    label: str
    start_date: date
    end_date: date
    status: Optional[str] = "DRAFT"


class AcademicYearOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    start_date: date
    end_date: date
    status: str
    term_count: Optional[int] = 0
    created_at: datetime


class TermCreate(BaseModel):
    academic_year_id: uuid.UUID
    name: str
    term_no: int
    start_date: date
    end_date: date
    enrolment_opens_at: Optional[datetime] = None
    enrolment_closes_at: Optional[datetime] = None
    is_current: Optional[bool] = False


class TermUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    enrolment_opens_at: Optional[datetime] = None
    enrolment_closes_at: Optional[datetime] = None
    is_current: Optional[bool] = None


class TermOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    academic_year_id: uuid.UUID
    name: str
    term_no: int
    start_date: date
    end_date: date
    enrolment_opens_at: Optional[datetime] = None
    enrolment_closes_at: Optional[datetime] = None
    is_current: bool
    created_at: datetime


class CalendarEventCreate(BaseModel):
    academic_year_id: uuid.UUID
    term_id: Optional[uuid.UUID] = None
    event_type: str  # 'HOLIDAY', 'EXAM_WINDOW', 'EVENT', 'ACADEMIC_DEADLINE'
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date


class CalendarEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    academic_year_id: uuid.UUID
    term_id: Optional[uuid.UUID] = None
    event_type: str
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    created_at: datetime


# Departments & Programmes
class DepartmentCreate(BaseModel):
    name: str
    code: str
    head_faculty_id: Optional[uuid.UUID] = None
    budget: Optional[Decimal] = Decimal("0.00")
    established_on: Optional[date] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    head_faculty_id: Optional[uuid.UUID] = None
    budget: Optional[Decimal] = None
    established_on: Optional[date] = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    head_faculty_id: Optional[uuid.UUID] = None
    head_faculty_name: Optional[str] = None
    budget: Optional[Decimal] = None
    established_on: Optional[date] = None
    programmes_count: Optional[int] = 0
    students_count: Optional[int] = 0


class ProgrammeCreate(BaseModel):
    department_id: uuid.UUID
    name: str
    code: str
    duration_terms: int = 8
    degree_level: str = "UNDERGRADUATE"


class ProgrammeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    department_id: uuid.UUID
    department_name: Optional[str] = None
    name: str
    code: str
    duration_terms: int
    degree_level: str


# Fees & Finance
class FeeStructureCreate(BaseModel):
    programme_id: uuid.UUID
    term_id: uuid.UUID
    name: str
    amount: Decimal
    due_date: date


class FeeStructureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    programme_id: uuid.UUID
    term_id: uuid.UUID
    programme_name: Optional[str] = None
    term_name: Optional[str] = None
    name: str
    amount: Decimal
    due_date: date


class BatchInvoicingRequest(BaseModel):
    fee_structure_id: Optional[uuid.UUID] = None
    programme_id: Optional[uuid.UUID] = None
    term_id: Optional[uuid.UUID] = None


class ScholarshipCreate(BaseModel):
    name: str
    kind: str  # PERCENT, FIXED
    value: Decimal
    criteria: Optional[str] = None


class AwardScholarshipRequest(BaseModel):
    scholarship_id: uuid.UUID
    term_id: uuid.UUID


# Rooms & Timetable
class RoomCreate(BaseModel):
    code: str
    room_type: str  # CLASSROOM, LAB, SEMINAR_HALL, AUDITORIUM
    capacity: int = 60
    building: str
    floor: int = 1


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    room_type: str
    capacity: int
    building: str
    floor: int


class TimetableSlotCreate(BaseModel):
    offering_id: uuid.UUID
    room_id: uuid.UUID
    faculty_id: Optional[uuid.UUID] = None
    day_of_week: str  # MONDAY, TUESDAY...
    start_time: time
    end_time: time


class TimetableSlotUpdate(BaseModel):
    room_id: Optional[uuid.UUID] = None
    faculty_id: Optional[uuid.UUID] = None
    day_of_week: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class TimetableSlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    room_id: uuid.UUID
    faculty_id: uuid.UUID
    day_of_week: str
    start_time: time
    end_time: time
    course_name: Optional[str] = None
    room_code: Optional[str] = None
    faculty_name: Optional[str] = None


# Broadcast Notifications
class BroadcastNotificationRequest(BaseModel):
    title: str
    message: str
    target_role: Optional[str] = "ALL"  # ADMIN, FACULTY, STUDENT, ALL
    event_type: str = "INSTITUTIONAL_ANNOUNCEMENT"
    channel: str = "IN_APP"


# Course Proposals & Approvals
class ProposalReviewRequest(BaseModel):
    action: str  # 'APPROVED' or 'REJECTED'
    remarks: Optional[str] = None


# Compliance Records
class ComplianceRecordCreate(BaseModel):
    requirement: str
    submission_date: date
    expiry_date: Optional[date] = None
    department_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None
    file_id: Optional[uuid.UUID] = None


# Grade Approval
class GradeBatchReviewRequest(BaseModel):
    action: Optional[str] = None  # 'APPROVED' or 'REJECTED'
    status: Optional[str] = None
    remarks: Optional[str] = None


# Analytics Report Generation
class AnalyticsReportGenerateRequest(BaseModel):
    report_type: str
    department_id: Optional[uuid.UUID] = None
    term_id: Optional[uuid.UUID] = None
    parameters: Optional[Dict[str, Any]] = None
