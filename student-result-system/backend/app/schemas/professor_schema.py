
from pydantic import BaseModel, EmailStr, Field


class ProfessorRegistration(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)

    employee_id: str = Field(min_length=1, max_length=20)
    designation: str = Field(min_length=1, max_length=100)
    department_code: str = Field(min_length=1, max_length=10)


class ProfessorUpdate(BaseModel):
    designation: str = Field(min_length=1, max_length=100)
    department_code: str = Field(min_length=1, max_length=10)


class ProfessorResponse(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    designation: str
    department_code: str
    department_name: str
