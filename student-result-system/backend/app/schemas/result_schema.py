from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AcademicSummaryResponse(BaseModel):
    student_id: int
    roll_no: str
    admission_year: int
    cgpa: Optional[Decimal] = None
    backlog_count: int


class TranscriptResponse(BaseModel):
    enrollment_id: int
    subject_code: str
    subject_name: str
    credits: int
    academic_year: str
    term: str
    semester_no: int
    attempt_no: int
    total_marks: Optional[Decimal] = None
    grade: Optional[str] = None
    grade_points: Optional[Decimal] = None
    result_status: str


class BacklogResponse(BaseModel):
    subject_code: str
    subject_name: str
    grade: str
    grade_points: Decimal
    academic_year: str
    term: str
    semester_no: int


class GradeScaleResponse(BaseModel):
    letter_grade: str
    min_marks: Optional[Decimal] = None
    grade_points: Decimal


class RevaluationCreate(BaseModel):
    enrollment_id: int
    component_id: int
    reason: str = Field(..., min_length=1)
    window_days: int = Field(default=15, ge=1, le=90)


class RevaluationResponse(BaseModel):
    request_id: int
    enrollment_id: int
    component_id: int
    reason: str
    old_marks: Decimal
    requested_at: datetime
    reviewed_by: Optional[int] = None
    decision: Optional[str] = None
    decided_at: Optional[datetime] = None
    revaluation_status: str


class RevaluationDecision(BaseModel):
    decision: Literal["Approved", "Rejected"]
    new_marks: Optional[Decimal] = Field(default=None, ge=0)
