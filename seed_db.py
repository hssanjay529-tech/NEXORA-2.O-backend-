"""
NEXORA Multi-Tenant Database Architecture — Database Seeding Script
===================================================================
Connects to local PostgreSQL (localhost:5432) and seeds realistic dummy data:
- 2 Colleges (Tenants)
- 2 Admins (1 per College)
- 10 Faculty members across departments
- 50 Students across departments and programmes
- Full relational hierarchy (Courses, Offerings, Enrollments, Timetable,
  Attendance, Assignments, Grades, Fees, Exams, Files, and Governance)
"""

import os
import sys
import uuid
import random
import logging
import argparse
from datetime import datetime, date, time, timedelta, timezone

# -----------------------------------------------------------------------------
# 0. Pure-Python Compatibility Fallback Hook (for Windows / Python 3.14 environments)
# -----------------------------------------------------------------------------
try:
    import importlib.util
    class _ForcePyLoader:
        @classmethod
        def find_spec(cls, fullname, path=None, target=None):
            if path:
                for p in path:
                    mod_name = fullname.split('.')[-1]
                    py_file = os.path.join(p, mod_name + '.py')
                    if os.path.isfile(py_file):
                        return importlib.util.spec_from_file_location(fullname, py_file)
            return None
    sys.meta_path.insert(0, _ForcePyLoader)
except Exception:
    pass

import sqlalchemy
from sqlalchemy import (
    create_engine, Column, String, Integer, Numeric, Boolean, Date, Time,
    DateTime, ForeignKey, Text, JSON, text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("seed_db")

Base = declarative_base()

# =============================================================================
# 1. SQLAlchemy ORM Models
# =============================================================================

class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default='ACTIVE')
    settings = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="tenant", cascade="all, delete-orphan")


class PlatformOperator(Base):
    __tablename__ = 'platform_operators'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default='ACTIVE')
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    role = Column(Text, nullable=False)  # 'ADMIN', 'FACULTY', 'STUDENT'
    email = Column(String, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    avatar_url = Column(Text)
    password_hash = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default='ACTIVE')
    last_login_at = Column(DateTime(timezone=True))
    failed_login_count = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="users")
    faculty_profile = relationship("Faculty", back_populates="user", uselist=False)
    student_profile = relationship("Student", back_populates="user", uselist=False)


class File(Base):
    __tablename__ = 'files'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    storage_key = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)
    mime_type = Column(Text, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(Text)
    kind = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Department(Base):
    __tablename__ = 'departments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    name = Column(Text, nullable=False)
    code = Column(Text, nullable=False)
    head_faculty_id = Column(UUID(as_uuid=True), ForeignKey('faculty.id', ondelete='SET NULL'))
    budget = Column(Numeric(12, 2), default=0.00)
    established_on = Column(Date)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="departments")
    faculty_members = relationship("Faculty", back_populates="department", foreign_keys="Faculty.department_id")
    programmes = relationship("Programme", back_populates="department")


class Faculty(Base):
    __tablename__ = 'faculty'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    employee_no = Column(Text, nullable=False)
    designation = Column(Text, nullable=False)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department", back_populates="faculty_members", foreign_keys=[department_id])


class Programme(Base):
    __tablename__ = 'programmes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    name = Column(Text, nullable=False)
    code = Column(Text, nullable=False)
    duration_terms = Column(Integer, default=8, nullable=False)
    degree_level = Column(Text, nullable=False)  # UNDERGRADUATE, POSTGRADUATE, DIPLOMA, DOCTORAL
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    department = relationship("Department", back_populates="programmes")
    students = relationship("Student", back_populates="programme")


class Student(Base):
    __tablename__ = 'students'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    programme_id = Column(UUID(as_uuid=True), ForeignKey('programmes.id', ondelete='RESTRICT'), nullable=False)
    roll_no = Column(Text, nullable=False)
    admission_year = Column(Integer, nullable=False)
    current_term_no = Column(Integer, default=1, nullable=False)
    status = Column(Text, default='ACTIVE', nullable=False)  # ACTIVE, SUSPENDED, ALUMNI, DROPPED
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="student_profile")
    programme = relationship("Programme", back_populates="students")


class AcademicYear(Base):
    __tablename__ = 'academic_years'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    label = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Text, default='DRAFT', nullable=False)
    published_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Term(Base):
    __tablename__ = 'terms'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False)
    name = Column(Text, nullable=False)
    term_no = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    enrolment_opens_at = Column(DateTime(timezone=True))
    enrolment_closes_at = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Room(Base):
    __tablename__ = 'rooms'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    code = Column(Text, nullable=False)
    room_type = Column(Text, nullable=False)  # CLASSROOM, LAB, SEMINAR_HALL, AUDITORIUM
    capacity = Column(Integer, default=60, nullable=False)
    building = Column(Text, nullable=False)
    floor = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Course(Base):
    __tablename__ = 'courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    course_code = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    credits = Column(Integer, default=3, nullable=False)
    syllabus_file_id = Column(UUID(as_uuid=True), ForeignKey('files.id', ondelete='SET NULL'))
    status = Column(Text, default='ACTIVE', nullable=False)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ProgrammeCourse(Base):
    __tablename__ = 'programme_courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    programme_id = Column(UUID(as_uuid=True), ForeignKey('programmes.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    term_no = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CourseOffering(Base):
    __tablename__ = 'course_offerings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    term_id = Column(UUID(as_uuid=True), ForeignKey('terms.id', ondelete='CASCADE'), nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey('faculty.id', ondelete='RESTRICT'), nullable=False)
    section = Column(Text, default='A', nullable=False)
    capacity = Column(Integer, default=60, nullable=False)
    status = Column(Text, default='ACTIVE', nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    status = Column(Text, default='ENROLLED', nullable=False)  # ENROLLED, DROPPED, COMPLETED
    enrolled_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CourseMaterial(Base):
    __tablename__ = 'course_materials'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='CASCADE'), nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey('files.id', ondelete='CASCADE'), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TimetableSlot(Base):
    __tablename__ = 'timetable_slots'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='CASCADE'), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey('rooms.id', ondelete='RESTRICT'), nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey('faculty.id', ondelete='RESTRICT'), nullable=False)
    day_of_week = Column(Text, nullable=False)  # MONDAY, TUESDAY...
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    att_date = Column(Date, nullable=False)
    status = Column(Text, nullable=False)  # PRESENT, ABSENT, LATE, EXCUSED
    marked_by = Column(UUID(as_uuid=True), ForeignKey('faculty.id', ondelete='SET NULL'))
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='CASCADE'), nullable=False)
    kind = Column(Text, nullable=False)  # ASSIGNMENT, QUIZ
    title = Column(Text, nullable=False)
    description = Column(Text)
    due_at = Column(DateTime(timezone=True), nullable=False)
    max_marks = Column(Numeric(5, 2), default=100.00, nullable=False)
    rubric_file_id = Column(UUID(as_uuid=True), ForeignKey('files.id', ondelete='SET NULL'))
    status = Column(Text, default='PUBLISHED', nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AssignmentSubmission(Base):
    __tablename__ = 'assignment_submissions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey('files.id', ondelete='SET NULL'))
    answers = Column(JSONB, default=dict)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    marks = Column(Numeric(5, 2))
    feedback = Column(Text)
    graded_by = Column(UUID(as_uuid=True), ForeignKey('faculty.id', ondelete='SET NULL'))
    status = Column(Text, default='SUBMITTED', nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class GradingScale(Base):
    __tablename__ = 'grading_scales'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    grade = Column(Text, nullable=False)
    min_marks = Column(Numeric(5, 2), nullable=False)
    max_marks = Column(Numeric(5, 2), nullable=False)
    grade_points = Column(Numeric(4, 2), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class GradeRecord(Base):
    __tablename__ = 'grade_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='CASCADE'), nullable=False)
    internal_marks = Column(Numeric(5, 2), default=0.00)
    final_marks = Column(Numeric(5, 2), default=0.00)
    # total_marks is GENERATED STORED in postgres
    grade = Column(Text)
    grade_points = Column(Numeric(4, 2))
    status = Column(Text, default='DRAFT', nullable=False)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey('faculty.id', ondelete='SET NULL'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class StudentTermResult(Base):
    __tablename__ = 'student_term_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    term_id = Column(UUID(as_uuid=True), ForeignKey('terms.id', ondelete='CASCADE'), nullable=False)
    sgpa = Column(Numeric(4, 2), nullable=False)
    cgpa = Column(Numeric(4, 2), nullable=False)
    credits_earned = Column(Integer, default=0, nullable=False)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FeeStructure(Base):
    __tablename__ = 'fee_structures'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    programme_id = Column(UUID(as_uuid=True), ForeignKey('programmes.id', ondelete='CASCADE'), nullable=False)
    term_id = Column(UUID(as_uuid=True), ForeignKey('terms.id', ondelete='CASCADE'), nullable=False)
    name = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FeeRecord(Base):
    __tablename__ = 'fee_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    fee_structure_id = Column(UUID(as_uuid=True), ForeignKey('fee_structures.id', ondelete='CASCADE'), nullable=False)
    amount_due = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0.00, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date)
    status = Column(Text, default='PENDING', nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    fee_record_id = Column(UUID(as_uuid=True), ForeignKey('fee_records.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(Text, nullable=False)  # CARD, UPI, NET_BANKING, CASH...
    gateway_ref = Column(Text, nullable=False)
    status = Column(Text, default='INITIATED', nullable=False)
    verified_at = Column(DateTime(timezone=True))
    receipt_file_id = Column(UUID(as_uuid=True), ForeignKey('files.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Exam(Base):
    __tablename__ = 'exams'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    term_id = Column(UUID(as_uuid=True), ForeignKey('terms.id', ondelete='CASCADE'), nullable=False)
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='CASCADE'), nullable=False)
    exam_type = Column(Text, nullable=False)  # MID_TERM, FINAL, LAB, RE_EXAM
    exam_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey('rooms.id', ondelete='SET NULL'))
    max_marks = Column(Numeric(5, 2), default=100.00, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ExamRegistration(Base):
    __tablename__ = 'exam_registrations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    exam_id = Column(UUID(as_uuid=True), ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    is_eligible = Column(Boolean, default=True, nullable=False)
    status = Column(Text, default='REGISTERED', nullable=False)
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    sent_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    offering_id = Column(UUID(as_uuid=True), ForeignKey('course_offerings.id', ondelete='SET NULL'))
    event_type = Column(Text, nullable=False)
    target_role = Column(Text)  # ADMIN, FACULTY, STUDENT, ALL
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# =============================================================================
# 2. Data Generators & Constants
# =============================================================================

# Standard Bcrypt hash for: Password123!
PASSWORD_HASH = "$2b$12$UVG4Rp46CEU1QNn3tTC52.72avfuZoRtg9RG44sWkPQO7Q5/1aH.O"

# Verified Bcrypt hash for: sanju$123
SANJU_PASSWORD_HASH = "$2b$12$o45LmGhmxajUmZsulz8yW.S27DPhagMujyi.9MIPMAClzo2Tjjjbm"

# Primary Student Account Configuration
PRIMARY_STUDENT = {
    "first_name": "Sanjay",
    "last_name": "H S",
    "email": "sanjudeepu.153@gmail.com",
    "password": "sanju$123",
    "password_hash": SANJU_PASSWORD_HASH,
}

# Replacement Student Roster (eliminating dummy names)
STUDENT_ROSTER = [
    ("Nirmala", "G"),
    ("Nisarga", "B G"),
    ("Nishanth", "C K"),
    ("Pavanraj", "Shetty S R"),
    ("Pooja", ""),
    ("Prajwal", "Gowda D"),
    ("Prarthana", "Ria R"),
    ("Preetham", "H A"),
    ("Prekshith", "M K"),
    ("Sahana", ""),
    ("Sanika", "C B"),
    ("Shalini", "M R"),
    ("Shashank", "H M"),
    ("Shreyas", "K M"),
    ("Shreyas", "V A"),
    ("Shwetha", "C S"),
    ("Soujanya", "H M"),
    ("Srujana", "K A"),
    ("Suprith", "T M"),
    ("Tarun", "Gowda A L"),
    ("Tejal", "Shekar"),
]


def generate_database_url() -> str:
    """Build PostgreSQL connection URL from environment or defaults."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    user = os.getenv("POSTGRES_USER", "nexora_admin")
    password = os.getenv("POSTGRES_PASSWORD", "nexora_password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "nexora")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"


def clear_existing_data(session):
    """Truncate tables in reverse dependency order."""
    logger.info("Cleaning existing data from database...")
    truncate_order = [
        "exam_registrations", "exams", "payments", "fee_records", "fee_structures",
        "student_term_results", "grade_records", "grading_scales", "assignment_submissions",
        "assignments", "attendance", "timetable_slots", "course_materials", "enrollments",
        "course_offerings", "programme_courses", "courses", "rooms", "terms", "academic_years",
        "students", "programmes", "faculty", "departments", "notifications",
        "files", "users", "platform_operators", "tenants"
    ]
    for table in truncate_order:
        try:
            session.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
        except Exception:
            pass
    session.commit()
    logger.info("Database cleaned successfully.")


def seed_database(db_url: str, reset: bool = True):
    """Primary seeding routine connecting to PostgreSQL and populating schema."""
    logger.info(f"Connecting to database at {db_url}...")
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if reset:
            clear_existing_data(session)

        # ---------------------------------------------------------------------
        # 1. Global Platform Operator
        # ---------------------------------------------------------------------
        logger.info("Seeding Global Platform Operator...")
        platform_op = PlatformOperator(
            id=uuid.UUID('00000000-0000-0000-0000-000000000001'),
            email='superadmin@nexoracloud.com',
            password_hash=PASSWORD_HASH,
            status='ACTIVE',
            created_at=datetime.now(timezone.utc)
        )
        session.add(platform_op)
        session.flush()

        # ---------------------------------------------------------------------
        # 2. Tenants (2 Colleges)
        # ---------------------------------------------------------------------
        logger.info("Seeding 2 Colleges (Tenants)...")
        t_apex_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
        t_metro_id = uuid.UUID('22222222-2222-2222-2222-222222222222')

        t_apex = Tenant(
            id=t_apex_id,
            slug='apex-institute',
            name='Apex Institute of Technology & Management',
            status='ACTIVE',
            settings={
                "currency": "INR",
                "timezone": "Asia/Kolkata",
                "branding": {
                    "logo_url": "https://assets.nexora.edu/branding/apex-logo.svg",
                    "primary_color": "#2563eb",
                    "college_code": "APEX-2026"
                },
                "thresholds": {
                    "min_attendance_pct": 75.0,
                    "passing_grade_pct": 40.0,
                    "max_course_credits_per_term": 26
                }
            }
        )

        t_metro = Tenant(
            id=t_metro_id,
            slug='metro-uni',
            name='Metropolitan University of Science & Technology',
            status='ACTIVE',
            settings={
                "currency": "INR",
                "timezone": "Asia/Kolkata",
                "branding": {
                    "logo_url": "https://assets.nexora.edu/branding/metro-logo.svg",
                    "primary_color": "#0d9488",
                    "college_code": "MUST-1998"
                },
                "thresholds": {
                    "min_attendance_pct": 80.0,
                    "passing_grade_pct": 45.0,
                    "max_course_credits_per_term": 28
                }
            }
        )

        session.add_all([t_apex, t_metro])
        session.flush()

        # ---------------------------------------------------------------------
        # 3. Admins (2 Admins, 1 per College)
        # ---------------------------------------------------------------------
        logger.info("Seeding 2 Admins (1 per College)...")
        u_admin_apex = User(
            id=uuid.UUID('aaaaaaaa-0000-0000-0000-000000000001'),
            tenant_id=t_apex_id,
            role='ADMIN',
            email='admin@apex.edu',
            first_name='Dr. Rajesh',
            last_name='Sharma',
            password_hash=PASSWORD_HASH,
            status='ACTIVE'
        )

        u_admin_metro = User(
            id=uuid.UUID('aaaaaaaa-0000-0000-0000-000000000002'),
            tenant_id=t_metro_id,
            role='ADMIN',
            email='admin@metro.edu',
            first_name='Dr. Vikramaditya',
            last_name='Sen',
            password_hash=PASSWORD_HASH,
            status='ACTIVE'
        )

        session.add_all([u_admin_apex, u_admin_metro])
        session.flush()

        # ---------------------------------------------------------------------
        # 4. Departments & Programmes
        # ---------------------------------------------------------------------
        logger.info("Seeding Departments & Academic Programmes...")
        # Apex Departments
        d_apex_cse = Department(id=uuid.UUID('bbbbbbbb-0000-0000-0000-000000000001'), tenant_id=t_apex_id, name='Department of Computer Science & Engineering', code='CSE', budget=15000000.00, established_on=date(2010, 6, 15))
        d_apex_ece = Department(id=uuid.UUID('bbbbbbbb-0000-0000-0000-000000000002'), tenant_id=t_apex_id, name='Department of Electronics & Communication Engineering', code='ECE', budget=12000000.00, established_on=date(2012, 8, 1))
        d_apex_me = Department(id=uuid.UUID('bbbbbbbb-0000-0000-0000-000000000003'), tenant_id=t_apex_id, name='Department of Mechanical Engineering', code='ME', budget=10000000.00, established_on=date(2014, 7, 20))

        # Metro Departments
        d_metro_cse = Department(id=uuid.UUID('bbbbbbbb-0000-0000-0000-000000000004'), tenant_id=t_metro_id, name='School of Computer Science & Engineering', code='CSE', budget=20000000.00, established_on=date(2005, 4, 10))
        d_metro_it = Department(id=uuid.UUID('bbbbbbbb-0000-0000-0000-000000000005'), tenant_id=t_metro_id, name='Department of Information Technology', code='IT', budget=14000000.00, established_on=date(2008, 9, 1))
        d_metro_dsai = Department(id=uuid.UUID('bbbbbbbb-0000-0000-0000-000000000006'), tenant_id=t_metro_id, name='Department of Data Science & Artificial Intelligence', code='DSAI', budget=18000000.00, established_on=date(2021, 1, 15))

        session.add_all([d_apex_cse, d_apex_ece, d_apex_me, d_metro_cse, d_metro_it, d_metro_dsai])
        session.flush()

        # Apex Programmes
        p_apex_btech_cse = Programme(id=uuid.UUID('dddddddd-0000-0000-0000-000000000001'), tenant_id=t_apex_id, department_id=d_apex_cse.id, name='Bachelor of Technology in Computer Science & Engineering', code='BTECH-CSE', duration_terms=8, degree_level='UNDERGRADUATE')
        p_apex_btech_ece = Programme(id=uuid.UUID('dddddddd-0000-0000-0000-000000000002'), tenant_id=t_apex_id, department_id=d_apex_ece.id, name='Bachelor of Technology in Electronics & Communication Engineering', code='BTECH-ECE', duration_terms=8, degree_level='UNDERGRADUATE')
        p_apex_mtech_ai = Programme(id=uuid.UUID('dddddddd-0000-0000-0000-000000000003'), tenant_id=t_apex_id, department_id=d_apex_cse.id, name='Master of Technology in Artificial Intelligence & Data Science', code='MTECH-AIDS', duration_terms=4, degree_level='POSTGRADUATE')

        # Metro Programmes
        p_metro_btech_cs = Programme(id=uuid.UUID('dddddddd-0000-0000-0000-000000000004'), tenant_id=t_metro_id, department_id=d_metro_cse.id, name='Bachelor of Technology in Computer Science', code='BTECH-CS', duration_terms=8, degree_level='UNDERGRADUATE')
        p_metro_btech_it = Programme(id=uuid.UUID('dddddddd-0000-0000-0000-000000000005'), tenant_id=t_metro_id, department_id=d_metro_it.id, name='Bachelor of Technology in Information Technology', code='BTECH-IT', duration_terms=8, degree_level='UNDERGRADUATE')
        p_metro_btech_dsai = Programme(id=uuid.UUID('dddddddd-0000-0000-0000-000000000006'), tenant_id=t_metro_id, department_id=d_metro_dsai.id, name='Bachelor of Technology in Data Science & Artificial Intelligence', code='BTECH-DSAI', duration_terms=8, degree_level='UNDERGRADUATE')

        session.add_all([p_apex_btech_cse, p_apex_btech_ece, p_apex_mtech_ai, p_metro_btech_cs, p_metro_btech_it, p_metro_btech_dsai])
        session.flush()

        # ---------------------------------------------------------------------
        # 5. Faculty Members (10 Faculty: 5 in Apex, 5 in Metro)
        # ---------------------------------------------------------------------
        logger.info("Seeding 10 Faculty Members across departments...")
        faculty_data = [
            # Apex Institute (5 Faculty)
            {
                "tenant_id": t_apex_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000011'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000001'),
                "email": "hod.cse@apex.edu", "first_name": "Dr. Aris", "last_name": "Thorne",
                "dept_id": d_apex_cse.id, "emp_no": "FAC-CSE-001", "designation": "Professor & Head of Department",
                "is_hod": True
            },
            {
                "tenant_id": t_apex_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000012'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000002'),
                "email": "prof.priya@apex.edu", "first_name": "Dr. Priya", "last_name": "Nair",
                "dept_id": d_apex_cse.id, "emp_no": "FAC-CSE-002", "designation": "Associate Professor",
                "is_hod": False
            },
            {
                "tenant_id": t_apex_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000013'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000003'),
                "email": "prof.amitabha@apex.edu", "first_name": "Dr. Amitabha", "last_name": "Roy",
                "dept_id": d_apex_cse.id, "emp_no": "FAC-CSE-003", "designation": "Assistant Professor",
                "is_hod": False
            },
            {
                "tenant_id": t_apex_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000014'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000004'),
                "email": "prof.vikram@apex.edu", "first_name": "Dr. Vikram", "last_name": "Malhotra",
                "dept_id": d_apex_ece.id, "emp_no": "FAC-ECE-001", "designation": "Professor & Head of Department",
                "is_hod": True
            },
            {
                "tenant_id": t_apex_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000015'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000005'),
                "email": "prof.sneha@apex.edu", "first_name": "Dr. Sneha", "last_name": "Kulkarni",
                "dept_id": d_apex_me.id, "emp_no": "FAC-ME-001", "designation": "Associate Professor & Head of Department",
                "is_hod": True
            },
            # Metro University (5 Faculty)
            {
                "tenant_id": t_metro_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000016'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000006'),
                "email": "hod.cse@metro.edu", "first_name": "Dr. Arvind", "last_name": "Menon",
                "dept_id": d_metro_cse.id, "emp_no": "FAC-CSE-101", "designation": "Professor & Dean",
                "is_hod": True
            },
            {
                "tenant_id": t_metro_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000017'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000007'),
                "email": "prof.shalini@metro.edu", "first_name": "Dr. Shalini", "last_name": "Mukherjee",
                "dept_id": d_metro_cse.id, "emp_no": "FAC-CSE-102", "designation": "Associate Professor",
                "is_hod": False
            },
            {
                "tenant_id": t_metro_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000018'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000008'),
                "email": "hod.it@metro.edu", "first_name": "Dr. Rahul", "last_name": "Deshmukh",
                "dept_id": d_metro_it.id, "emp_no": "FAC-IT-101", "designation": "Professor & Head of Department",
                "is_hod": True
            },
            {
                "tenant_id": t_metro_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000019'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000009'),
                "email": "prof.meera@metro.edu", "first_name": "Dr. Meera", "last_name": "Nambiar",
                "dept_id": d_metro_it.id, "emp_no": "FAC-IT-102", "designation": "Assistant Professor",
                "is_hod": False
            },
            {
                "tenant_id": t_metro_id,
                "user_id": uuid.UUID('aaaaaaaa-0000-0000-0000-000000000020'),
                "faculty_id": uuid.UUID('cccccccc-0000-0000-0000-000000000010'),
                "email": "hod.dsai@metro.edu", "first_name": "Dr. Karthik", "last_name": "Raman",
                "dept_id": d_metro_dsai.id, "emp_no": "FAC-DSAI-101", "designation": "Professor & Head of Department",
                "is_hod": True
            }
        ]

        faculty_records = []
        for f in faculty_data:
            f_user = User(
                id=f["user_id"],
                tenant_id=f["tenant_id"],
                role='FACULTY',
                email=f["email"],
                first_name=f["first_name"],
                last_name=f["last_name"],
                password_hash=PASSWORD_HASH,
                status='ACTIVE'
            )
            session.add(f_user)
            session.flush()

            fac = Faculty(
                id=f["faculty_id"],
                tenant_id=f["tenant_id"],
                user_id=f_user.id,
                department_id=f["dept_id"],
                employee_no=f["emp_no"],
                designation=f["designation"]
            )
            session.add(fac)
            faculty_records.append(fac)

        session.flush()

        # Update HOD links on departments
        d_apex_cse.head_faculty_id = faculty_records[0].id
        d_apex_ece.head_faculty_id = faculty_records[3].id
        d_apex_me.head_faculty_id = faculty_records[4].id
        d_metro_cse.head_faculty_id = faculty_records[5].id
        d_metro_it.head_faculty_id = faculty_records[7].id
        d_metro_dsai.head_faculty_id = faculty_records[9].id
        session.flush()

        # ---------------------------------------------------------------------
        # 6. Academic Calendar (Years, Terms, Rooms)
        # ---------------------------------------------------------------------
        logger.info("Seeding Academic Years, Terms, and Campus Rooms...")
        # Academic Years
        ay_apex = AcademicYear(id=uuid.UUID('ffffffff-0000-0000-0000-000000000001'), tenant_id=t_apex_id, label='2026-27', start_date=date(2026, 7, 1), end_date=date(2027, 6, 30), status='PUBLISHED', published_by=u_admin_apex.id, published_at=datetime.now(timezone.utc))
        ay_metro = AcademicYear(id=uuid.UUID('ffffffff-0000-0000-0000-000000000002'), tenant_id=t_metro_id, label='2026-27', start_date=date(2026, 7, 1), end_date=date(2027, 6, 30), status='PUBLISHED', published_by=u_admin_metro.id, published_at=datetime.now(timezone.utc))
        session.add_all([ay_apex, ay_metro])
        session.flush()

        # Terms
        term_apex_fall = Term(id=uuid.UUID('10101010-0000-0000-0000-000000000001'), tenant_id=t_apex_id, academic_year_id=ay_apex.id, name='Fall 2026 (Semester 5)', term_no=5, start_date=date(2026, 8, 1), end_date=date(2026, 12, 15), is_current=True)
        term_apex_spring = Term(id=uuid.UUID('10101010-0000-0000-0000-000000000002'), tenant_id=t_apex_id, academic_year_id=ay_apex.id, name='Spring 2027 (Semester 6)', term_no=6, start_date=date(2027, 1, 5), end_date=date(2027, 5, 20), is_current=False)
        term_metro_fall = Term(id=uuid.UUID('10101010-0000-0000-0000-000000000003'), tenant_id=t_metro_id, academic_year_id=ay_metro.id, name='Fall 2026 (Term 5)', term_no=5, start_date=date(2026, 8, 1), end_date=date(2026, 12, 15), is_current=True)
        term_metro_spring = Term(id=uuid.UUID('10101010-0000-0000-0000-000000000004'), tenant_id=t_metro_id, academic_year_id=ay_metro.id, name='Spring 2027 (Term 6)', term_no=6, start_date=date(2027, 1, 5), end_date=date(2027, 5, 20), is_current=False)
        session.add_all([term_apex_fall, term_apex_spring, term_metro_fall, term_metro_spring])
        session.flush()

        # Rooms
        rooms = [
            Room(id=uuid.UUID('20202020-0000-0000-0000-000000000001'), tenant_id=t_apex_id, code='LH-101', room_type='CLASSROOM', capacity=80, building='Aryabhata Block', floor=1),
            Room(id=uuid.UUID('20202020-0000-0000-0000-000000000002'), tenant_id=t_apex_id, code='LAB-204', room_type='LAB', capacity=40, building='Turing Complex', floor=2),
            Room(id=uuid.UUID('20202020-0000-0000-0000-000000000003'), tenant_id=t_apex_id, code='AUD-01', room_type='AUDITORIUM', capacity=300, building='Main Administration', floor=1),
            Room(id=uuid.UUID('20202020-0000-0000-0000-000000000004'), tenant_id=t_metro_id, code='CR-301', room_type='CLASSROOM', capacity=70, building='Science Block A', floor=3),
            Room(id=uuid.UUID('20202020-0000-0000-0000-000000000005'), tenant_id=t_metro_id, code='AI-LAB-1', room_type='LAB', capacity=45, building='Innovation Tower', floor=4)
        ]
        session.add_all(rooms)
        session.flush()

        # ---------------------------------------------------------------------
        # 7. Courses, Programme Courses & Course Offerings
        # ---------------------------------------------------------------------
        logger.info("Seeding Courses, Curriculums, and Course Offerings...")
        # Apex Courses
        c_apex_dbms = Course(id=uuid.UUID('40404040-0000-0000-0000-000000000001'), tenant_id=t_apex_id, department_id=d_apex_cse.id, course_code='CS301', title='Database Management Systems', credits=4, status='ACTIVE')
        c_apex_os = Course(id=uuid.UUID('40404040-0000-0000-0000-000000000002'), tenant_id=t_apex_id, department_id=d_apex_cse.id, course_code='CS302', title='Operating Systems & Architecture', credits=4, status='ACTIVE')
        c_apex_dsp = Course(id=uuid.UUID('40404040-0000-0000-0000-000000000003'), tenant_id=t_apex_id, department_id=d_apex_ece.id, course_code='EC301', title='Digital Signal Processing', credits=4, status='ACTIVE')
        c_apex_thermo = Course(id=uuid.UUID('40404040-0000-0000-0000-000000000004'), tenant_id=t_apex_id, department_id=d_apex_me.id, course_code='ME301', title='Applied Thermodynamics', credits=4, status='ACTIVE')

        # Metro Courses
        c_metro_ds = Course(id=uuid.UUID('40404040-0000-0000-0000-000000000005'), tenant_id=t_metro_id, department_id=d_metro_cse.id, course_code='CS-311', title='Advanced Data Structures & Algorithms', credits=4, status='ACTIVE')
        c_metro_web = Course(id=uuid.UUID('40404040-0000-0000-0000-000000000006'), tenant_id=t_metro_id, department_id=d_metro_it.id, course_code='IT-321', title='Full Stack Web Technologies', credits=4, status='ACTIVE')
        c_metro_ml = Course(id=uuid.UUID('40404040-0000-0000-0000-000000000007'), tenant_id=t_metro_id, department_id=d_metro_dsai.id, course_code='DS-331', title='Machine Learning & Neural Networks', credits=4, status='ACTIVE')

        session.add_all([c_apex_dbms, c_apex_os, c_apex_dsp, c_apex_thermo, c_metro_ds, c_metro_web, c_metro_ml])
        session.flush()

        # Programme Courses
        prog_courses = [
            ProgrammeCourse(tenant_id=t_apex_id, programme_id=p_apex_btech_cse.id, course_id=c_apex_dbms.id, term_no=5, is_mandatory=True),
            ProgrammeCourse(tenant_id=t_apex_id, programme_id=p_apex_btech_cse.id, course_id=c_apex_os.id, term_no=5, is_mandatory=True),
            ProgrammeCourse(tenant_id=t_apex_id, programme_id=p_apex_btech_ece.id, course_id=c_apex_dsp.id, term_no=5, is_mandatory=True),
            ProgrammeCourse(tenant_id=t_apex_id, programme_id=p_apex_mtech_ai.id, course_id=c_apex_dbms.id, term_no=1, is_mandatory=True),
            ProgrammeCourse(tenant_id=t_metro_id, programme_id=p_metro_btech_cs.id, course_id=c_metro_ds.id, term_no=5, is_mandatory=True),
            ProgrammeCourse(tenant_id=t_metro_id, programme_id=p_metro_btech_it.id, course_id=c_metro_web.id, term_no=5, is_mandatory=True),
            ProgrammeCourse(tenant_id=t_metro_id, programme_id=p_metro_btech_dsai.id, course_id=c_metro_ml.id, term_no=5, is_mandatory=True),
        ]
        session.add_all(prog_courses)
        session.flush()

        # Course Offerings
        off_apex_dbms = CourseOffering(id=uuid.UUID('50505050-0000-0000-0000-000000000001'), tenant_id=t_apex_id, course_id=c_apex_dbms.id, term_id=term_apex_fall.id, faculty_id=faculty_records[0].id, section='A', capacity=60, status='ACTIVE')
        off_apex_os = CourseOffering(id=uuid.UUID('50505050-0000-0000-0000-000000000002'), tenant_id=t_apex_id, course_id=c_apex_os.id, term_id=term_apex_fall.id, faculty_id=faculty_records[1].id, section='A', capacity=60, status='ACTIVE')
        off_apex_dsp = CourseOffering(id=uuid.UUID('50505050-0000-0000-0000-000000000003'), tenant_id=t_apex_id, course_id=c_apex_dsp.id, term_id=term_apex_fall.id, faculty_id=faculty_records[3].id, section='A', capacity=60, status='ACTIVE')
        off_metro_ds = CourseOffering(id=uuid.UUID('50505050-0000-0000-0000-000000000004'), tenant_id=t_metro_id, course_id=c_metro_ds.id, term_id=term_metro_fall.id, faculty_id=faculty_records[5].id, section='A', capacity=60, status='ACTIVE')
        off_metro_web = CourseOffering(id=uuid.UUID('50505050-0000-0000-0000-000000000005'), tenant_id=t_metro_id, course_id=c_metro_web.id, term_id=term_metro_fall.id, faculty_id=faculty_records[7].id, section='A', capacity=60, status='ACTIVE')
        off_metro_ml = CourseOffering(id=uuid.UUID('50505050-0000-0000-0000-000000000006'), tenant_id=t_metro_id, course_id=c_metro_ml.id, term_id=term_metro_fall.id, faculty_id=faculty_records[9].id, section='A', capacity=60, status='ACTIVE')

        session.add_all([off_apex_dbms, off_apex_os, off_apex_dsp, off_metro_ds, off_metro_web, off_metro_ml])
        session.flush()

        # Timetable slots
        timetable_slots = [
            TimetableSlot(tenant_id=t_apex_id, offering_id=off_apex_dbms.id, room_id=rooms[0].id, faculty_id=faculty_records[0].id, day_of_week='MONDAY', start_time=time(9, 0), end_time=time(10, 30)),
            TimetableSlot(tenant_id=t_apex_id, offering_id=off_apex_os.id, room_id=rooms[0].id, faculty_id=faculty_records[1].id, day_of_week='TUESDAY', start_time=time(11, 0), end_time=time(12, 30)),
            TimetableSlot(tenant_id=t_apex_id, offering_id=off_apex_dsp.id, room_id=rooms[1].id, faculty_id=faculty_records[3].id, day_of_week='WEDNESDAY', start_time=time(14, 0), end_time=time(15, 30)),
            TimetableSlot(tenant_id=t_metro_id, offering_id=off_metro_ds.id, room_id=rooms[3].id, faculty_id=faculty_records[5].id, day_of_week='MONDAY', start_time=time(9, 30), end_time=time(11, 0)),
            TimetableSlot(tenant_id=t_metro_id, offering_id=off_metro_web.id, room_id=rooms[3].id, faculty_id=faculty_records[7].id, day_of_week='THURSDAY', start_time=time(10, 0), end_time=time(11, 30)),
            TimetableSlot(tenant_id=t_metro_id, offering_id=off_metro_ml.id, room_id=rooms[4].id, faculty_id=faculty_records[9].id, day_of_week='FRIDAY', start_time=time(14, 0), end_time=time(16, 0)),
        ]
        session.add_all(timetable_slots)
        session.flush()

        # ---------------------------------------------------------------------
        # 8. Students (50 Students across departments)
        # ---------------------------------------------------------------------
        logger.info("Seeding 50 Students across departments and programmes...")
        # 25 in Apex, 25 in Metro
        # Apex: 15 CSE, 6 ECE, 4 AI
        # Metro: 10 CS, 8 IT, 7 DSAI
        student_configs = []

        # Apex 25
        for i in range(1, 16):
            student_configs.append({
                "tenant_id": t_apex_id, "prog": p_apex_btech_cse,
                "roll": f"2024CSE{i:03d}", "domain": "apex.edu", "offering": off_apex_dbms, "offering_aux": off_apex_os
            })
        for i in range(1, 7):
            student_configs.append({
                "tenant_id": t_apex_id, "prog": p_apex_btech_ece,
                "roll": f"2024ECE{i:03d}", "domain": "apex.edu", "offering": off_apex_dsp, "offering_aux": None
            })
        for i in range(1, 5):
            student_configs.append({
                "tenant_id": t_apex_id, "prog": p_apex_mtech_ai,
                "roll": f"2024AI{i:03d}", "domain": "apex.edu", "offering": off_apex_dbms, "offering_aux": None
            })

        # Metro 25
        for i in range(1, 11):
            student_configs.append({
                "tenant_id": t_metro_id, "prog": p_metro_btech_cs,
                "roll": f"2024CS{i+100:03d}", "domain": "metro.edu", "offering": off_metro_ds, "offering_aux": None
            })
        for i in range(1, 9):
            student_configs.append({
                "tenant_id": t_metro_id, "prog": p_metro_btech_it,
                "roll": f"2024IT{i+100:03d}", "domain": "metro.edu", "offering": off_metro_web, "offering_aux": None
            })
        for i in range(1, 8):
            student_configs.append({
                "tenant_id": t_metro_id, "prog": p_metro_btech_dsai,
                "roll": f"2024DS{i+100:03d}", "domain": "metro.edu", "offering": off_metro_ml, "offering_aux": None
            })

        students = []
        enrollments = []
        for idx, cfg in enumerate(student_configs):
            if idx == 0:
                first_name = PRIMARY_STUDENT["first_name"]
                last_name = PRIMARY_STUDENT["last_name"]
                email = PRIMARY_STUDENT["email"]
                pwd_hash = PRIMARY_STUDENT["password_hash"]
            else:
                r_idx = (idx - 1) % len(STUDENT_ROSTER)
                first_name, last_name = STUDENT_ROSTER[r_idx]
                clean_name = f"{first_name.lower()}.{last_name.replace(' ', '').lower()}" if last_name else first_name.lower()
                email = f"student.{clean_name}{idx+1}@{cfg['domain']}"
                pwd_hash = PASSWORD_HASH

            user_uuid = uuid.UUID(f"eeeeeeee-0000-0000-0000-{idx+1:012d}")
            student_uuid = uuid.UUID(f"eeeeeeee-1111-0000-0000-{idx+1:012d}")

            s_user = User(
                id=user_uuid,
                tenant_id=cfg["tenant_id"],
                role='STUDENT',
                email=email,
                first_name=first_name,
                last_name=last_name,
                password_hash=pwd_hash,
                status='ACTIVE'
            )
            session.add(s_user)
            session.flush()

            student = Student(
                id=student_uuid,
                tenant_id=cfg["tenant_id"],
                user_id=s_user.id,
                programme_id=cfg["prog"].id,
                roll_no=cfg["roll"],
                admission_year=2024,
                current_term_no=5,
                status='ACTIVE'
            )
            session.add(student)
            students.append(student)

        session.flush()

        # Create student course enrollments
        for idx, cfg in enumerate(student_configs):
            student = students[idx]
            # Primary course enrollment
            enrollments.append(
                Enrollment(
                    tenant_id=cfg["tenant_id"],
                    offering_id=cfg["offering"].id,
                    student_id=student.id,
                    status='ENROLLED'
                )
            )
            # Aux course enrollment if available
            if cfg["offering_aux"]:
                enrollments.append(
                    Enrollment(
                        tenant_id=cfg["tenant_id"],
                        offering_id=cfg["offering_aux"].id,
                        student_id=student.id,
                        status='ENROLLED'
                    )
                )

        session.add_all(enrollments)
        session.flush()

        # ---------------------------------------------------------------------
        # 9. Attendance & Assessment Records
        # ---------------------------------------------------------------------
        logger.info("Seeding Attendance records and Assessment activities...")
        attendance_dates = [
            date(2026, 8, 10), date(2026, 8, 17), date(2026, 8, 24),
            date(2026, 9, 1), date(2026, 9, 8), date(2026, 9, 15)
        ]
        attendance_records = []
        for enr in enrollments:
            for att_d in attendance_dates:
                status_choice = random.choices(['PRESENT', 'PRESENT', 'PRESENT', 'ABSENT', 'LATE'], weights=[70, 15, 5, 5, 5])[0]
                attendance_records.append(
                    Attendance(
                        tenant_id=enr.tenant_id,
                        offering_id=enr.offering_id,
                        student_id=enr.student_id,
                        att_date=att_d,
                        status=status_choice
                    )
                )
        session.add_all(attendance_records)
        session.flush()

        # Assignments
        asg_dbms_1 = Assignment(
            id=uuid.UUID('60606060-0000-0000-0000-000000000001'),
            tenant_id=t_apex_id,
            offering_id=off_apex_dbms.id,
            kind='ASSIGNMENT',
            title='Relational Schema Design & Normalization Project',
            description='Design 3NF schemas for enterprise e-commerce backend with BCNF proofs.',
            due_at=datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc),
            max_marks=100.00,
            status='PUBLISHED',
            created_by=u_admin_apex.id
        )
        asg_ds_1 = Assignment(
            id=uuid.UUID('60606060-0000-0000-0000-000000000002'),
            tenant_id=t_metro_id,
            offering_id=off_metro_ds.id,
            kind='ASSIGNMENT',
            title='Red-Black Tree and B-Tree Performance Analysis',
            description='Implement and benchmark cache locality of Balanced Search Trees in C++.',
            due_at=datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc),
            max_marks=100.00,
            status='PUBLISHED',
            created_by=u_admin_metro.id
        )
        session.add_all([asg_dbms_1, asg_ds_1])
        session.flush()

        # Submissions for first 10 students of each offering
        submissions = []
        for student in students[:10]:
            submissions.append(
                AssignmentSubmission(
                    tenant_id=t_apex_id,
                    assignment_id=asg_dbms_1.id,
                    student_id=student.id,
                    marks=88.50,
                    feedback='Excellent schema normalization and diagram clarity.',
                    status='GRADED'
                )
            )
        for student in students[25:35]:
            submissions.append(
                AssignmentSubmission(
                    tenant_id=t_metro_id,
                    assignment_id=asg_ds_1.id,
                    student_id=student.id,
                    marks=92.00,
                    feedback='Comprehensive benchmarking results and clean implementation.',
                    status='GRADED'
                )
            )
        session.add_all(submissions)
        session.flush()

        # ---------------------------------------------------------------------
        # 10. Grading Scales, Grade Records & Term Results
        # ---------------------------------------------------------------------
        logger.info("Seeding Grading Scales and Academic Grade Records...")
        grade_scales = [
            GradingScale(tenant_id=t_apex_id, grade='O', min_marks=90, max_marks=100, grade_points=10.0, description='Outstanding'),
            GradingScale(tenant_id=t_apex_id, grade='A+', min_marks=80, max_marks=89.99, grade_points=9.0, description='Excellent'),
            GradingScale(tenant_id=t_apex_id, grade='A', min_marks=70, max_marks=79.99, grade_points=8.0, description='Very Good'),
            GradingScale(tenant_id=t_apex_id, grade='B+', min_marks=60, max_marks=69.99, grade_points=7.0, description='Good'),
            GradingScale(tenant_id=t_apex_id, grade='B', min_marks=50, max_marks=59.99, grade_points=6.0, description='Above Average'),
            GradingScale(tenant_id=t_apex_id, grade='C', min_marks=40, max_marks=49.99, grade_points=5.0, description='Pass'),
            GradingScale(tenant_id=t_apex_id, grade='F', min_marks=0, max_marks=39.99, grade_points=0.0, description='Fail'),
            # Metro
            GradingScale(tenant_id=t_metro_id, grade='A+', min_marks=90, max_marks=100, grade_points=10.0, description='Outstanding'),
            GradingScale(tenant_id=t_metro_id, grade='A', min_marks=80, max_marks=89.99, grade_points=9.0, description='Excellent'),
            GradingScale(tenant_id=t_metro_id, grade='B', min_marks=70, max_marks=79.99, grade_points=8.0, description='Good'),
            GradingScale(tenant_id=t_metro_id, grade='C', min_marks=50, max_marks=69.99, grade_points=6.0, description='Average'),
            GradingScale(tenant_id=t_metro_id, grade='F', min_marks=0, max_marks=49.99, grade_points=0.0, description='Fail'),
        ]
        session.add_all(grade_scales)
        session.flush()

        grade_records = []
        for enr in enrollments[:20]:
            grade_records.append(
                GradeRecord(
                    tenant_id=enr.tenant_id,
                    student_id=enr.student_id,
                    offering_id=enr.offering_id,
                    internal_marks=38.00,
                    final_marks=48.00,
                    grade='A+',
                    grade_points=9.0,
                    status='APPROVED',
                    published_at=datetime.now(timezone.utc)
                )
            )
        session.add_all(grade_records)
        session.flush()

        term_results = []
        for s in students[:25]:
            term_results.append(
                StudentTermResult(
                    tenant_id=t_apex_id,
                    student_id=s.id,
                    term_id=term_apex_fall.id,
                    sgpa=8.85,
                    cgpa=8.70,
                    credits_earned=22,
                    published_at=datetime.now(timezone.utc)
                )
            )
        for s in students[25:]:
            term_results.append(
                StudentTermResult(
                    tenant_id=t_metro_id,
                    student_id=s.id,
                    term_id=term_metro_fall.id,
                    sgpa=9.10,
                    cgpa=8.95,
                    credits_earned=24,
                    published_at=datetime.now(timezone.utc)
                )
            )
        session.add_all(term_results)
        session.flush()

        # ---------------------------------------------------------------------
        # 11. Finance & Fee Structures
        # ---------------------------------------------------------------------
        logger.info("Seeding Fee Structures, Records & Payment Receipts...")
        fee_struct_apex = FeeStructure(
            id=uuid.UUID('70707070-0000-0000-0000-000000000001'),
            tenant_id=t_apex_id,
            programme_id=p_apex_btech_cse.id,
            term_id=term_apex_fall.id,
            name='Tuition & Laboratory Fee (Fall 2026)',
            amount=85000.00,
            due_date=date(2026, 8, 30)
        )
        fee_struct_metro = FeeStructure(
            id=uuid.UUID('70707070-0000-0000-0000-000000000002'),
            tenant_id=t_metro_id,
            programme_id=p_metro_btech_cs.id,
            term_id=term_metro_fall.id,
            name='Semester Academic & Facility Fee (Fall 2026)',
            amount=95000.00,
            due_date=date(2026, 8, 30)
        )
        session.add_all([fee_struct_apex, fee_struct_metro])
        session.flush()

        fee_records = []
        payments = []
        for s in students[:15]:
            fr = FeeRecord(
                tenant_id=t_apex_id,
                student_id=s.id,
                fee_structure_id=fee_struct_apex.id,
                amount_due=85000.00,
                discount=0.00,
                due_date=date(2026, 8, 30),
                paid_date=date(2026, 8, 20),
                status='PAID'
            )
            session.add(fr)
            session.flush()
            fee_records.append(fr)

            payments.append(
                Payment(
                    tenant_id=t_apex_id,
                    fee_record_id=fr.id,
                    amount=85000.00,
                    method='UPI',
                    gateway_ref=f"PAY-APEX-UPI-{s.roll_no}",
                    status='VERIFIED',
                    verified_at=datetime.now(timezone.utc)
                )
            )

        for s in students[25:35]:
            fr = FeeRecord(
                tenant_id=t_metro_id,
                student_id=s.id,
                fee_structure_id=fee_struct_metro.id,
                amount_due=95000.00,
                discount=5000.00,
                due_date=date(2026, 8, 30),
                paid_date=date(2026, 8, 22),
                status='PAID'
            )
            session.add(fr)
            session.flush()
            fee_records.append(fr)

            payments.append(
                Payment(
                    tenant_id=t_metro_id,
                    fee_record_id=fr.id,
                    amount=90000.00,
                    method='NET_BANKING',
                    gateway_ref=f"PAY-METRO-NET-{s.roll_no}",
                    status='VERIFIED',
                    verified_at=datetime.now(timezone.utc)
                )
            )

        session.add_all(payments)
        session.flush()

        # ---------------------------------------------------------------------
        # 12. Examination Management
        # ---------------------------------------------------------------------
        logger.info("Seeding Examination Schedules and Student Registrations...")
        exam_apex = Exam(
            id=uuid.UUID('80808080-0000-0000-0000-000000000001'),
            tenant_id=t_apex_id,
            term_id=term_apex_fall.id,
            offering_id=off_apex_dbms.id,
            exam_type='MID_TERM',
            exam_date=date(2026, 10, 12),
            start_time=time(10, 0),
            end_time=time(12, 0),
            room_id=rooms[0].id,
            max_marks=50.00
        )
        exam_metro = Exam(
            id=uuid.UUID('80808080-0000-0000-0000-000000000002'),
            tenant_id=t_metro_id,
            term_id=term_metro_fall.id,
            offering_id=off_metro_ds.id,
            exam_type='MID_TERM',
            exam_date=date(2026, 10, 14),
            start_time=time(14, 0),
            end_time=time(16, 0),
            room_id=rooms[3].id,
            max_marks=50.00
        )
        session.add_all([exam_apex, exam_metro])
        session.flush()

        exam_regs = []
        for s in students[:15]:
            exam_regs.append(
                ExamRegistration(
                    tenant_id=t_apex_id,
                    exam_id=exam_apex.id,
                    student_id=s.id,
                    is_eligible=True,
                    status='APPROVED'
                )
            )
        for s in students[25:35]:
            exam_regs.append(
                ExamRegistration(
                    tenant_id=t_metro_id,
                    exam_id=exam_metro.id,
                    student_id=s.id,
                    is_eligible=True,
                    status='APPROVED'
                )
            )
        session.add_all(exam_regs)
        session.flush()

        # ---------------------------------------------------------------------
        # 13. System Notifications & Broadcasts
        # ---------------------------------------------------------------------
        logger.info("Seeding Notifications & Announcements...")
        notifications = [
            Notification(
                tenant_id=t_apex_id,
                sent_by=u_admin_apex.id,
                event_type='CAMPUS_ANNOUNCEMENT',
                target_role='ALL',
                title='Welcome to Academic Year 2026-27',
                message='All students and faculty are requested to verify their timetable and laboratory assignments.'
            ),
            Notification(
                tenant_id=t_metro_id,
                sent_by=u_admin_metro.id,
                event_type='EXAM_SCHEDULE',
                target_role='STUDENT',
                title='Mid-Term Examination Dates Published',
                message='The Mid-Term exam window opens on October 10. Check the portal for hall ticket downloads.'
            )
        ]
        session.add_all(notifications)
        session.flush()

        session.commit()

        # ---------------------------------------------------------------------
        # 14. Seeding Summary Report
        # ---------------------------------------------------------------------
        total_tenants = session.query(Tenant).count()
        total_users = session.query(User).count()
        total_admins = session.query(User).filter(User.role == 'ADMIN').count()
        total_faculty = session.query(Faculty).count()
        total_students = session.query(Student).count()
        total_depts = session.query(Department).count()
        total_programmes = session.query(Programme).count()
        total_courses = session.query(Course).count()
        total_offerings = session.query(CourseOffering).count()
        total_enrollments = session.query(Enrollment).count()
        total_attendance = session.query(Attendance).count()

        print("\n" + "="*70)
        print("  [+] NEXORA DATABASE SEEDING COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"  * Colleges (Tenants)       : {total_tenants}")
        print(f"  * Total Users Seeded       : {total_users} (Superadmin + {total_users-1} Campus Users)")
        print(f"  * Admins                   : {total_admins} (1 per College)")
        print(f"  * Faculty Members          : {total_faculty} (5 per College)")
        print(f"  * Students Seeded          : {total_students} (25 per College across Departments)")
        print(f"  * Departments              : {total_depts}")
        print(f"  * Academic Programmes      : {total_programmes}")
        print(f"  * Courses Defined          : {total_courses}")
        print(f"  * Course Offerings         : {total_offerings}")
        print(f"  * Student Enrollments      : {total_enrollments}")
        print(f"  * Attendance Logs          : {total_attendance}")
        print("="*70)
        print("  [*] Standard Test Account Credentials:")
        print("     - Student (Sanjay H S) : sanjudeepu.153@gmail.com (Password: sanju$123)")
        print("     - Platform Superadmin  : superadmin@nexoracloud.com (Password: Password123!)")
        print("     - Apex Admin           : admin@apex.edu (Password: Password123!)")
        print("     - Metro Admin          : admin@metro.edu (Password: Password123!)")
        print("     - Apex CSE HOD         : hod.cse@apex.edu (Password: Password123!)")
        print("     - Metro CSE HOD        : hod.cse@metro.edu (Password: Password123!)")
        print("="*70 + "\n")

    except Exception as e:
        session.rollback()
        logger.error(f"Seeding failed due to error: {e}", exc_info=True)
        raise
    finally:
        session.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Seed NEXORA PostgreSQL database with realistic dummy data.")
    parser.add_argument("--db-url", type=str, default=None, help="PostgreSQL connection string (defaults to env or localhost:5432)")
    parser.add_argument("--no-reset", action="store_true", help="Do not truncate existing data before seeding")
    args = parser.parse_args()

    url = args.db_url or generate_database_url()
    seed_database(db_url=url, reset=not args.no_reset)
