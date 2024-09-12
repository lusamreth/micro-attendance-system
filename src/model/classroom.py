import sqlite3
import uuid
from collections.abc import Callable
from datetime import datetime

from pydantic import BaseModel


# to calculate end time =
class Classroom(BaseModel):
    id: str
    lecturer_name: str
    subject_name: str
    duration: int
    lecture_time: float
    late_penalty_duration: float
    record_interval: float | None

    @classmethod
    def parse_sql(cls, row: tuple) -> "Classroom":
        return cls(
            id=row[0],
            lecturer_name=row[1],
            subject_name=row[2],
            duration=row[3],
            lecture_time=row[4],
            late_penalty_duration=row[5],
            record_interval=row[6],
        )


def create_classroom(
    lecturer_name: str,
    subject_name: str,
    duration: int,
    late_penalty_duration: float,
    record_interval: float = 5 * 60,
    lecture_time: float | None = None,
) -> Classroom:
    lect = (
        datetime.now().timestamp()
        if lecture_time is None or lecture_time == 0
        else lecture_time
    )

    classroom_id = str(uuid.uuid4())
    return Classroom(
        id=classroom_id,
        lecturer_name=lecturer_name,
        subject_name=subject_name,
        duration=duration,
        lecture_time=lect,
        late_penalty_duration=late_penalty_duration,
        record_interval=record_interval,
    )


class ClassroomModifiable(BaseModel):
    subject_name: str | None
    duration: int | None
    lecture_time: float | None
    late_penalty_duration: float | None
    record_interval: float | None


def update_classroom(old: Classroom, modified: ClassroomModifiable) -> Classroom:
    return Classroom(
        id=old.id,
        lecturer_name=old.lecturer_name,
        subject_name=(
            modified.subject_name
            if modified.subject_name is not None
            else old.subject_name
        ),
        duration=modified.duration if modified.duration is not None else old.duration,
        lecture_time=(
            modified.lecture_time
            if modified.lecture_time is not None
            else old.lecture_time
        ),
        late_penalty_duration=(
            modified.late_penalty_duration
            if modified.late_penalty_duration is not None
            else old.late_penalty_duration
        ),
        record_interval=(
            modified.record_interval
            if modified.record_interval is not None
            else old.record_interval
        ),
    )


class ClassroomDBHandler:
    def __init__(self, conn: Callable[..., sqlite3.Connection]):
        self.connect = conn

    def init_table(self):
        with self.connect() as conn:
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS `classroom`(
                        id TEXT NOT NULL,
                        lecturer_name TEXT NOT NULL,
                        subject_name TEXT NOT NULL,
                        duration INTEGER NOT NULL,
                        lecture_time FLOAT NOT NULL,
                        late_penalty_duration FLOAT NOT NULL,
                        record_interval FLOAT NOT NULL,
                        PRIMARY KEY (id)
                    )
                """
            )
            conn.commit()

    def create_many(self, classroom_list: list[Classroom]):
        with self.connect() as conn:
            for classroom in classroom_list:
                conn.execute(
                    """
                        INSERT INTO "classroom" (id, lecturer_name, subject_name, duration, 
                                                 lecture_time, late_penalty_duration, record_interval) 
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        classroom.id,
                        classroom.lecturer_name,
                        classroom.subject_name,
                        classroom.duration,
                        classroom.lecture_time,
                        classroom.late_penalty_duration,
                        classroom.record_interval,
                    ),
                )
            conn.commit()
            return classroom_list

    def insert(self, classroom: Classroom):
        with self.connect() as conn:
            conn.execute(
                """
                    INSERT INTO "classroom" (id, lecturer_name, subject_name, duration, 
                                             lecture_time, late_penalty_duration, record_interval) 
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    classroom.id,
                    classroom.lecturer_name,
                    classroom.subject_name,
                    classroom.duration,
                    classroom.lecture_time,
                    classroom.late_penalty_duration,
                    classroom.record_interval,
                ),
            )
            conn.commit()

    def update(self, id: str, modified: ClassroomModifiable):
        old = self.get(id)
        if old is None:
            raise Exception("Classroom not found")

        updated = update_classroom(old, modified)
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE classroom
                SET subject_name = ?,
                    duration = ?,
                    lecture_time = ?,
                    late_penalty_duration = ?,
                    record_interval = ?
                WHERE id = ?
                """,
                (
                    updated.subject_name,
                    updated.duration,
                    updated.lecture_time,
                    updated.late_penalty_duration,
                    updated.record_interval,
                    updated.id,
                ),
            )
            conn.commit()

    def delete(self, id: str):
        with self.connect() as conn:
            exec = conn.execute("DELETE FROM classroom WHERE id = ?", (id,))
            conn.commit()
            print(exec.rowcount)
            return exec.rowcount

    def get(self, id: str) -> Classroom | None:
        with self.connect() as conn:
            single_res = conn.execute("SELECT * FROM classroom WHERE id = ?", (id,))
            row = single_res.fetchone()
            if row:
                result = Classroom.parse_sql(row)
                return result
            return None

    def list(self) -> list[Classroom]:
        with self.connect() as conn:
            raw_list = conn.execute("SELECT * FROM classroom")
            rows = raw_list.fetchall()
            result = []
            for row in rows:
                result.append(Classroom.parse_sql(row))
            return result
