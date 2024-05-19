import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.exceptions import init_global_exception_handlers
from src.route.providers.base import (
    get_attendance_db,
    get_classroom_db,
    get_enrollment_db,
    get_student_db,
)
from src.route.v1.router import init_router

app = FastAPI()

init_router(app.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stud_db = get_student_db()
attd_db = get_attendance_db()
class_db = get_classroom_db()
enroll_db = get_enrollment_db()

stud_db.init_table()
attd_db.init_table()
class_db.init_table()
enroll_db.init_table()

init_global_exception_handlers(app)


def main() -> None:
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
