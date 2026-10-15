import uuid
from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


# Course Materials
class CourseMaterialCreate(BaseModel):
    course_offering_id: uuid.UUID
    title: str
    description: Optional[str] = None
    file_id: uuid.UUID


class CourseMaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    file_id: uuid.UUID
    title: str
    description: Optional[str] = None
    created_at: datetime
    file_name: Optional[str] = None
    mime_type: Optional[str] = None


# Attendance
class AttendanceSessionCreate(BaseModel):
    course_offering_id: uuid.UUID
    session_date: date
    timetable_slot_id: Optional[uuid.UUID] = None
    topic_covered: Optional[str] = None


class AttendanceRecordItem(BaseModel):
    student_id: uuid.UUID
    status: str  # PRESENT, ABSENT, LATE, EXCUSED
    remarks: Optional[str] = None


class AttendanceBatchRecordRequest(BaseModel):
    offering_id: Optional[uuid.UUID] = None
    att_date: date
    records: List[AttendanceRecordItem]


# Assignments & Quizzes
class AssignmentCreate(BaseModel):
    course_offering_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_at: datetime
    max_marks: Optional[Decimal] = Decimal("100.00")
    rubric_file_id: Optional[uuid.UUID] = None


# Quiz Models
class QuizQuestionItem(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str
    marks: Decimal = Decimal("1.00")


class QuizCreate(BaseModel):
    course_offering_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_at: datetime
    duration_minutes: Optional[int] = 60
    questions: List[QuizQuestionItem]


class GradeSubmissionRequest(BaseModel):
    marks: Decimal
    feedback: Optional[str] = None


# Grades Management
class GradeBatchEntryItem(BaseModel):
    student_id: uuid.UUID
    internal_marks: Optional[Decimal] = Decimal("0.00")
    final_marks: Optional[Decimal] = Decimal("0.00")
    grade: Optional[str] = None
    grade_points: Optional[Decimal] = None


class GradeBatchEntryRequest(BaseModel):
    offering_id: uuid.UUID
    entries: List[GradeBatchEntryItem]


class SubmitGradeApprovalRequest(BaseModel):
    offering_id: Optional[uuid.UUID] = None
    course_code: Optional[str] = None
    remarks: Optional[str] = None


# Academic Flags
class AcademicFlagCreate(BaseModel):
    student_id: uuid.UUID
    offering_id: Optional[uuid.UUID] = None
    flag_type: str  # ATTENDANCE, ACADEMIC, PLAGIARISM, MISCONDUCT, WELFARE, PERFORMANCE
    description: str


# Discussions
class DiscussionThreadCreate(BaseModel):
    course_offering_id: uuid.UUID
    title: str
    is_locked: Optional[bool] = False


class DiscussionPostCreate(BaseModel):
    thread_id: uuid.UUID
    content: str
    parent_post_id: Optional[uuid.UUID] = None


# Operational Requests
class TimetableChangeRequestCreate(BaseModel):
    slot_id: uuid.UUID
    requested_day: str
    requested_start: time
    requested_end: time
    reason: str


class LeaveApplicationCreate(BaseModel):
    leave_type: str  # CASUAL, SICK, EARNED, DUTY, MATERNITY, SABBATICAL
    start_date: date
    end_date: date
    reason: str


class FacultyCourseProposalCreate(BaseModel):
    title: str
    department_id: uuid.UUID
    course_code: str
    credits: int = 3
    description: Optional[str] = None
    syllabus_file_id: Optional[uuid.UUID] = None
