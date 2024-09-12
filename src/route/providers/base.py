from src.db import init_db_root, open_db
from src.model.attendance import AttendanceDBHandler
from src.model.attendance_detail import AttendanceDetailDBHandler
from src.model.classroom import ClassroomDBHandler
from src.model.enrollments import EnrollmentDBHandler
from src.model.student import StudentDBHandler

init_db_root()
connection = open_db()


def get_student_db():
    studentDB = StudentDBHandler(conn=open_db)
    return studentDB


def get_attendance_db():
    attendanceDB = AttendanceDBHandler(conn=open_db)
    return attendanceDB


def get_classroom_db():
    attendanceDB = ClassroomDBHandler(conn=open_db)
    return attendanceDB


def get_enrollment_db():
    enrollmentDB = EnrollmentDBHandler(conn=open_db)
    return enrollmentDB


def get_stats_db():
    enrollmentDB = AttendanceDetailDBHandler(conn=open_db)
    return enrollmentDB
