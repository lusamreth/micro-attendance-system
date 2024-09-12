from fastapi import APIRouter, Depends

from src.model.attendance import Attendance, AttendanceJoinStudent, create_attd
from src.response import ErrorTemplate, ResponseTemplate
from src.route.providers.base import (
    get_attendance_db,
    get_enrollment_db,
    get_stats_db,
    get_student_db,
)
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


@attendance_router.get(
    "/classroom/subject/{subject_name}",
    # response_model=ResponseTemplate[list[AttendanceJoinStudent]],
)
def list_attendance_by_subject(subject_name, service=Depends(get_attendance_db)):
    res = service.get_by_subject(subject_name)
    return ResponseTemplate(
        res,
        "Successfully retrieved attendance",
    )


@attendance_router.post("/")
def take_attendance(
    attendance_data: list[CreateAttendance],
    stat_db=Depends(get_stats_db),
    service=Depends(get_attendance_db),
):
    attendances = []
    for attend in attendance_data:
        attendances.append(create_attd(**attend.model_dump()))

    res = service.create_many(attendances)
    print("ress")
    for attendance in res:
        stat_db.consolidate(attendance.id, attendance.punctuality)

    return ResponseTemplate(res, "Successfully attend attendance")


@attendance_router.post(
    "/mark-as-permission/{attendance_id}",
    response_model=ResponseTemplate[bool],
)
def mark_absent_as_perm(
    attd_id: str,
    stat_db=Depends(get_stats_db),
    attendance_db=Depends(get_attendance_db),
    enrol_db=Depends(get_enrollment_db),
):

    attendance = attendance_db.get(attd_id)
    if attendance is None:
        return ErrorTemplate(
            "No attendance is founded.".format(attd_id),
            "Retrieval error",
        ).to_json()

    enrollment = enrol_db.get(attendance.enrollment_id)
    if enrollment is None:
        return ErrorTemplate(
            "Fatal failure???".format(attd_id),
            "Retrieval error",
        ).to_json()

    res = stat_db.mark_permission(enrollment.student_id)
    # print("rr", res)
    if not res:
        return ErrorTemplate(
            "failed to marked permission of student with this id {}".format(attd_id),
            "Retrieval error",
        ).to_json()

    return ResponseTemplate(
        res,
        "Marked permission of enrollment with id {}".format(attd_id),
    ).to_json()


@attendance_router.get(
    "/student/{student_id}",
    # response_model=ResponseTemplate[list[AttendanceJoinStudent]],
)
def list_attendance_by_subject(student_id, service=Depends(get_attendance_db)):
    res = service.get_by_student(student_id)
    return ResponseTemplate(
        res,
        "Successfully retrieved attendance",
    )
