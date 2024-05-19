from fastapi import APIRouter

from .attendance import attendance_router
from .classroom import classroom_router
from .student import student_router


def init_router(app: APIRouter):
    app.include_router(student_router, prefix="/students", tags=["students"])
    app.include_router(attendance_router, prefix="/attendances", tags=["attendances"])
    app.include_router(classroom_router, prefix="/classrooms", tags=["classrooms"])
