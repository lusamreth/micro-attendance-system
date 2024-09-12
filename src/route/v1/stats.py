from fastapi import APIRouter, Depends

from src.model.attendance_detail import AttendanceDetail
from src.model.enrollments import Enrollment
from src.response import ErrorTemplate, ResponseTemplate
from src.route.providers.base import get_attendance_db, get_enrollment_db, get_stats_db

stat_router = APIRouter()


@stat_router.get("/{student_id}", response_model=ResponseTemplate[AttendanceDetail])
def list_attendance_by_student(student_id, service=Depends(get_stats_db)):
    res = service.get_by_student_id(student_id)
    if res is None:
        return ErrorTemplate([], "Cannot found attendance details", 404)

    return ResponseTemplate(res, "bruh")


@stat_router.get("/", response_model=ResponseTemplate[list[AttendanceDetail]])
def list_attendance_by_student_full(student_id, service=Depends(get_stats_db)):
    res = service.get_by_student_id(student_id)
    if res is None:
        return ErrorTemplate([], "Cannot found attendance details", 404)

    return ResponseTemplate(res, "bruh")


@stat_router.get(
    "/enrollment/{class_id}", response_model=ResponseTemplate[list[Enrollment]]
)
def list_enrollment_by_class(class_id, service=Depends(get_enrollment_db)):
    res = get_enrollment_db().get_by_class(class_id)
    if res is None:
        return ErrorTemplate([], "Cannot found enrollment details by class", 404)

    return ResponseTemplate(res, "bruh")
