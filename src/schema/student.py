from typing import Optional

from pydantic import BaseModel


class CreateStudent(BaseModel):
    firstname: str
    lastname: str | None = None
    # classroom: str
    generation: int
    gender: str | None = None
    phone_num: str | None = None
    major: str | None = None
    gender: str | None = None


class EnrollStudent(BaseModel):
    student_id: str
    class_id: str


class UpdateStudent(BaseModel):
    # classroom: int
    generation: int


class DeleleStudent(BaseModel):
    id: str
    name: str | None


class MarkStudentPermission(BaseModel):
    attendance_id: str
