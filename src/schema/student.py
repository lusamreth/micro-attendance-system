from typing import Optional

from pydantic import BaseModel


class CreateStudent(BaseModel):
    firstname: str
    lastname: str
    # classroom: str
    generation: int
    gender: str


class EnrollStudent(BaseModel):
    student_id: str
    class_id: str


class UpdateStudent(BaseModel):
    # classroom: int
    generation: int


class DeleleStudent(BaseModel):
    id: str
    name: str | None
