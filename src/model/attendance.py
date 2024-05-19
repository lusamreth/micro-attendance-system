import sqlite3
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


def justify_punctuality(attendance: Attendance, classroom: Classroom):
    lect_end_time = classroom.lecture_time
    acceptable_late = classroom.late_penalty_duration
    entry_time = attendance.entry_time
    latable_time = acceptable_late + lect_end_time
    punc = attendance.punctuality
    print(
        "ENNN",
        datetime.fromtimestamp(entry_time),
        datetime.fromtimestamp(lect_end_time),
    )

    if entry_time >= (classroom.duration + lect_end_time):
        punc = Punctuality.ABSENT
        return str(punc)

    if entry_time > latable_time:
        punc = Punctuality.LATE
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
        last_record=modified.last_record
        if modified.last_record is not None
        else old.last_record,
        entry_time=modified.entry_time
        if modified.entry_time is not None
        else old.entry_time,
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
