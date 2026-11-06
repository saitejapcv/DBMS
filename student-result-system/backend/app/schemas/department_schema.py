
from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    department_code: str = Field(
        min_length=1,
        max_length=10
    )
    department_name: str = Field(
        min_length=1,
        max_length=100
    )


class DepartmentUpdate(BaseModel):
    department_name: str = Field(
        min_length=1,
        max_length=100
    )


class DepartmentResponse(BaseModel):
    department_code: str
    department_name: str
    head_professor_id: int | None = None


class DepartmentHeadUpdate(BaseModel):
    head_professor_id: int = Field(gt=0)

