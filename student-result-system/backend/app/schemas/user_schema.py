from pydantic import BaseModel, EmailStr, Field, model_validator


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    name: str
    role: str


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_admin: bool | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        return self
