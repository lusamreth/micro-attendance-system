from typing import Optional

from pydantic import BaseModel


class CreateClassroom(BaseModel):
    lecturer_name: str
    duration: int
    lecture_time: float
    late_penalty_duration: float
    subject_name: str


class UpdateClassroom(BaseModel):
    duration: Optional[int] = None
    lecture_time: Optional[float] = None
    late_penalty_duration: Optional[float] = None


class DeleteClassroom(BaseModel):
    id: str
    lecturer_name: Optional[str] = None
