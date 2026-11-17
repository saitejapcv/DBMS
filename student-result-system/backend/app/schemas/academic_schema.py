from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, Field


# --- TEACHING ASSIGNMENTS ---
class TeachingAssignmentCreate(BaseModel):
    subject_code: str = Field(..., max_length=20)
    professor_id: int
    academic_year: str = Field(..., max_length=10)
    term: Literal["ODD", "EVEN", "SUMMER"]


class TeachingAssignmentResponse(BaseModel):
    assignment_id: int
    subject_code: str
    professor_id: int
    academic_year: str
    term: str
    submitted_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


# --- ENROLLMENTS ---
class EnrollmentCreate(BaseModel):
    student_id: int


class EnrollmentResponse(BaseModel):
    enrollment_id: int
    student_id: int
    assignment_id: int
    enrolled_on: date
    grade: Optional[str] = None


# --- EVALUATION COMPONENTS ---
class EvaluationComponentCreate(BaseModel):
    name: str = Field(..., max_length=100)
    max_marks: Decimal = Field(..., gt=0)
    weightage: Decimal = Field(..., ge=1, le=100)


class EvaluationComponentResponse(BaseModel):
    component_id: int
    assignment_id: int
    name: str
    max_marks: Decimal
    weightage: Decimal


# --- MARKS ---
class MarkItem(BaseModel):
    enrollment_id: int
    marks_obtained: Decimal = Field(..., ge=0)


class BulkMarksRequest(BaseModel):
    component_id: int
    marks: list[MarkItem]


class MarkResponse(BaseModel):
    enrollment_id: int
    student_id: int
    component_id: int
    marks_obtained: Decimal
    entered_at: datetime