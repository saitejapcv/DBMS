
from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    subject_code: str = Field(
        min_length=1,
        max_length=20
    )

    subject_name: str = Field(
        min_length=1,
        max_length=150
    )

    credits: int = Field(gt=0)

    department_code: str = Field(
        min_length=1,
        max_length=10
    )


class SubjectUpdate(BaseModel):
    subject_name: str = Field(
        min_length=1,
        max_length=150
    )

    credits: int = Field(gt=0)

    department_code: str = Field(
        min_length=1,
        max_length=10
    )


class SubjectResponse(BaseModel):
    subject_code: str
    subject_name: str
    credits: int
    department_code: str
    department_name: str
