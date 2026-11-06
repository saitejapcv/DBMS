from pydantic import BaseModel, EmailStr, Field

class StudentResponse(BaseModel):
    roll_no: str
    name: str
    email: EmailStr
    admission_year: int
    current_semester: int
    cgpa: float
    backlog_count: int
    department_name: str

class StudentCreate(BaseModel):
    roll_no: str = Field(min_length=1, max_length=20)
    admission_year: int = Field(ge=2000)
    current_semester: int = Field(ge=1, le=12)
    department_code: str = Field(min_length=1, max_length=10)

class StudentRegistration(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    roll_no: str = Field(min_length=1, max_length=20)
    admission_year: int = Field(ge=2000)
    current_semester: int = Field(ge=1, le=12)
    department_code: str = Field(min_length=1, max_length=10)

class StudentUpdate(BaseModel):
    current_semester: int = Field(ge=1, le=12)
    department_code: str = Field(min_length=1, max_length=10)