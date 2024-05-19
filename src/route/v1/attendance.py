from fastapi import APIRouter, Depends

from src.model.attendance import Attendance, create_attd
from src.response import ResponseTemplate
from src.route.providers.base import get_attendance_db
from src.schema.attendance import CreateAttendance

attendance_router = APIRouter()


@attendance_router.get("/", response_model=ResponseTemplate[list[Attendance]])
def list_attendance(service=Depends(get_attendance_db)):
    res = service.list_attendance()
    return ResponseTemplate(res, "Successfully retrieved attendance")


@attendance_router.get(
    "/classroom/{class_id}", response_model=ResponseTemplate[list[Attendance]]
)
def list_attendance_by_class(class_id, service=Depends(get_attendance_db)):
    res = service.list_by_classroom(class_id)
    return ResponseTemplate(res, "Successfully retrieved attendance")


@attendance_router.post("/")
def take_attendance(
    attendance_data: list[CreateAttendance], service=Depends(get_attendance_db)
):
    attendances = []
    for attend in attendance_data:
        attendances.append(create_attd(**attend.model_dump()))

    res = service.create_many(attendances)
    return ResponseTemplate(res, "Successfully attend attendance")
