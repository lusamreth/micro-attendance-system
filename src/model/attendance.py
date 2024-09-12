import sqlite3
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from src.model.classroom import Classroom, ClassroomModifiable
from src.model.model_exception import NotFoundError
from src.model.utils import check_constraints


class Punctuality(str, Enum):
    LATE = "late"
    ONTIME = "ontime"
    ABSENT = "absent"
    AUTO = "auto"

    def __str__(self):
        return self.value


class Attendance(BaseModel):
    id: str
    enrollment_id: str
    last_record: float
    entry_time: float
    punctuality: Punctuality


class AttendanceJoinStudent(BaseModel):
    id: str
    enrollment_id: str
    last_record: float
    entry_time: float
    punctuality: Punctuality
    firstname: str
    lastname: str


class AttendanceJoinClass(Classroom):
    id: str
    enrollment_id: str
    last_record: float
    entry_time: float
    punctuality: Punctuality


def create_attd(
    enrollment_id,
    last_record,
    entry_time,
    punctuality=Punctuality.AUTO,
) -> Attendance:
    attd_id = str(uuid.uuid4())
    entry_time = datetime.now().timestamp()
    return Attendance(
        id=attd_id,
        enrollment_id=enrollment_id,
        last_record=last_record,
        entry_time=entry_time,
        punctuality=punctuality,
    )


from datetime import datetime


def ts_hour_greater(ts1, ts2, equal=False):
    dto1 = datetime.fromtimestamp(ts1)
    dto2 = datetime.fromtimestamp(ts2)
    if equal:
        return dto1.hour >= dto2.hour
    return dto1.hour > dto2.hour


def ts_minute_greater(ts1, ts2, equal=False):
    dto1 = datetime.fromtimestamp(ts1)
    dto2 = datetime.fromtimestamp(ts2)

    if equal:
        return dto1.minute >= dto2.minute
    return dto1.minute > dto2.minute


def justify_punctuality(attendance: Attendance, classroom: Classroom):
    # lecture_time could be like 5:00 or 12:00 (0->23)
    lect_end_time = classroom.lecture_time  # hours + minutes -> minutes
    acceptable_late = classroom.late_penalty_duration
    entry_time = attendance.entry_time
    latable_time = acceptable_late + lect_end_time
    punc = attendance.punctuality
    entry_dto = datetime.fromtimestamp(entry_time)
    lect_dto = datetime.fromtimestamp(lect_end_time)
    print(
        "ENNN",
        datetime.fromtimestamp(entry_time),
        datetime.fromtimestamp(lect_end_time),
    )

    # Check if the entry time is in the same hour as the lecture end time
    if entry_dto.hour == lect_dto.hour:
        # Check if the entry time is after the lecture end time
        if entry_dto.minute > lect_dto.minute:
            # Check if the entry time is within the acceptable late period
            if entry_dto.minute <= (lect_dto.minute + latable_time):
                punc = Punctuality.LATE
            else:
                punc = Punctuality.ABSENT
        else:
            punc = Punctuality.ONTIME
    else:
        # Handle the case where the entry time and lecture end time are in different hours
        if entry_dto.hour > lect_dto.hour:
            punc = Punctuality.ABSENT
        else:
            punc = Punctuality.ONTIME

    if punc == Punctuality.AUTO:
        punc = Punctuality.ONTIME

    return str(punc)


class AttendanceModifiable(BaseModel):
    last_record: float
    entry_time: float


def update_attd(old: Attendance, modified: AttendanceModifiable) -> Attendance:
    return Attendance(
        id=old.id,
        enrollment_id=old.enrollment_id,
        last_record=(
            modified.last_record
            if modified.last_record is not None
            else old.last_record
        ),
        entry_time=(
            modified.entry_time if modified.entry_time is not None else old.entry_time
        ),
        punctuality=old.punctuality,
    )


class AttendanceDBHandler:
    def __init__(self, conn: Callable[..., sqlite3.Connection]):
        self.connect = conn

    def init_table(self):
        with self.connect() as conn:
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS `attendance`(
                        id TEXT NOT NULL,
                        enrollment_id TEXT NOT NULL,
                        last_record FLOAT NOT NULL,
                        entry_time FLOAT NOT NULL,
                        punctuality TEXT NOT NULL,
                        PRIMARY KEY (id),
                        FOREIGN KEY(enrollment_id) REFERENCES enrollment(id)
                    )
                """
            )
            conn.commit()

    def create_many(self, attendance_list: list[Attendance]):
        with self.connect() as conn:
            modified = []
            for attendance in attendance_list:
                check_constraints(conn, "enrollment", attendance.enrollment_id)
                # Retrieve classroom using enrollment_id
                classroom_res = conn.execute(
                    """
                    SELECT c.* FROM classroom c
                    JOIN enrollment e ON c.id = e.class_id
                    WHERE e.id = ?
                    """,
                    (attendance.enrollment_id,),
                ).fetchone()

                classroom = Classroom.parse_sql(classroom_res)
                punc = justify_punctuality(attendance, classroom)

                conn.execute(
                    """
                        INSERT INTO "attendance" (id, enrollment_id, last_record,
                                                  entry_time, punctuality) 
                        VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        attendance.id,
                        attendance.enrollment_id,
                        attendance.last_record,
                        attendance.entry_time,
                        punc,
                    ),
                )
                modified.append(
                    Attendance(**{**attendance.model_dump(), "punctuality": punc})
                )
            conn.commit()
            return modified

    def create(self, attendance: Attendance):
        with self.connect() as conn:
            check_constraints(conn, "enrollment", attendance.enrollment_id)
            # Retrieve classroom using enrollment_id
            classroom_res = conn.execute(
                """
                SELECT c.* FROM classroom c
                JOIN enrollment e ON c.id = e.class_id
                WHERE e.id = ?
                """,
                (attendance.enrollment_id,),
            ).fetchone()

            classroom = Classroom.parse_sql(classroom_res)
            punc = justify_punctuality(attendance, classroom)

            conn.execute(
                """
                    INSERT INTO "attendance" (id, enrollment_id, last_record,
                                              entry_time, punctuality) 
                    VALUES (?, ?, ?, ?, ?);
                """,
                (
                    attendance.id,
                    attendance.enrollment_id,
                    attendance.last_record,
                    attendance.entry_time,
                    punc,
                ),
            )
            conn.commit()
            return attendance

    def update(self, id: str, modified: AttendanceModifiable):
        old = self.get(id)
        if old is None:
            raise NotFoundError("Attendance not found")

        updated = update_attd(old, modified)
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE attendance
                SET last_record = ?,
                    entry_time = ?
                WHERE id = ?
                """,
                (
                    updated.last_record,
                    updated.entry_time,
                    updated.id,
                ),
            )
            conn.commit()
            return updated

    def delete(self, id: str):
        with self.connect() as conn:
            exec = conn.execute("DELETE FROM attendance WHERE id = ?", (id,))
            conn.commit()
            return exec.rowcount

    def get(self, id: str):
        with self.connect() as conn:
            single_res = conn.execute("SELECT * FROM attendance WHERE id = ?", (id,))
            row = single_res.fetchone()
            if row:
                result = Attendance(
                    id=row[0],
                    enrollment_id=row[1],
                    last_record=row[2],
                    entry_time=row[3],
                    punctuality=row[4],
                )
                return result
            return None

    def get_by_subject(self, subject: str):
        with self.connect() as conn:
            # attendance.id,enrollment.id,entry_time,last_record,punctuality,student.firstname,student.lastname
            single_res = conn.execute(
                """
                    SELECT
                    attendance.id,enrollment.id,entry_time,last_record,punctuality,student.firstname,student.lastname,classroom.subject_name
                    FROM attendance 
                    JOIN enrollment ON enrollment.id = attendance.enrollment_id
                    JOIN student ON student.id = enrollment.student_id
                    JOIN classroom ON classroom.id = enrollment.class_id
                    WHERE subject_name = ?
                """,
                (subject,),
            )
            row = single_res.fetchone()

            if row:
                result = AttendanceJoinStudent(
                    id=row[0],
                    enrollment_id=row[1],
                    last_record=row[2],
                    entry_time=row[3],
                    punctuality=row[4],
                    firstname=row[5],
                    lastname=row[6],
                )
                return result
            return None

    def get_by_student(self, student_id) -> list[Attendance]:
        with self.connect() as conn:
            # attendance.id,enrollment.id,entry_time,last_record,punctuality,student.firstname,student.lastname
            single_res = conn.execute(
                """
                    SELECT * FROM attendance 
                    JOIN enrollment e ON e.id = attendance.enrollment_id
                    JOIN student s ON s.id = e.student_id
                    WHERE s.id = ?
                """,
                (student_id,),
            )

            rows = single_res.fetchall()
            results = []
            if rows:
                for row in rows:
                    result = Attendance(
                        id=row[0],
                        enrollment_id=row[1],
                        last_record=row[2],
                        entry_time=row[3],
                        punctuality=row[4],
                    )
                    results.append(result)
            return results

    def list_attendance(self) -> list[Attendance]:
        with self.connect() as conn:
            raw_list = conn.execute("SELECT * FROM attendance")
            rows = raw_list.fetchall()
            result = []
            for row in rows:
                result.append(
                    Attendance(
                        id=row[0],
                        enrollment_id=row[1],
                        last_record=row[2],
                        entry_time=row[3],
                        punctuality=row[4],
                    )
                )
            return result

    def list_by_classroom(self, class_id: str) -> list[AttendanceJoinClass]:
        with self.connect() as conn:
            raw_list = conn.execute(
                """
                    SELECT * FROM attendance 
                    JOIN enrollment ON enrollment.id = attendance.enrollment_id 
                    JOIN classroom ON classroom.id = enrollment.class_id
                    WHERE classroom.id = ?
                """,
                (class_id,),
            )
            rows = raw_list.fetchall()
            result = []
            for row in rows:
                print(row)
                joined = Classroom.parse_sql(row[8:]).model_dump()
                del joined["id"]
                result.append(
                    AttendanceJoinClass(
                        id=row[0],
                        enrollment_id=row[1],
                        last_record=row[2],
                        entry_time=row[3],
                        punctuality=row[4],
                        **joined
                    )
                )
            return result
