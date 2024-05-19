from pydantic import BaseModel


class CreateAttendance(BaseModel):
    last_record: float
    entry_time: float
    enrollment_id: str


class UpdateAttendance(BaseModel):
    last_record: float
    entry_time: float
