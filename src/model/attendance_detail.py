import sqlite3
import uuid
from collections.abc import Callable
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.model.attendance import Punctuality


class AttendanceDetail(BaseModel):
    id: str
    absent_count: int
    absent_with_permission: int
    present_count: int
    late_count: int
    student_id: str


def create_attendance_detail(
    student_id: str,
    absent_count: int = 0,
    absent_with_permission: int = 0,
    present_count: int = 0,
    late_count: int = 0,
) -> AttendanceDetail:
    attendance_id = str(uuid.uuid4())
    print("DUMA", student_id, absent_count)
    return AttendanceDetail(
        id=attendance_id,
        absent_count=absent_count,
        absent_with_permission=absent_with_permission,
        present_count=present_count,
        late_count=late_count,
        student_id=student_id,
    )


class AttendanceDetailModifiable(BaseModel):
    absent_count: Optional[int] = None
    absent_with_permission: Optional[int] = None
    present_count: Optional[int] = None
    late_count: Optional[int] = None


def update_attendance_detail(
    old: AttendanceDetail, modified: AttendanceDetailModifiable
) -> AttendanceDetail:
    return AttendanceDetail(
        id=old.id,
        absent_count=(
            modified.absent_count
            if modified.absent_count is not None
            else old.absent_count
        ),
        absent_with_permission=(
            modified.absent_with_permission
            if modified.absent_with_permission is not None
            else old.absent_with_permission
        ),
        present_count=(
            modified.present_count
            if modified.present_count is not None
            else old.present_count
        ),
        late_count=(
            modified.late_count if modified.late_count is not None else old.late_count
        ),
        student_id=old.student_id,
    )


class AttendanceDetailDBHandler:
    def __init__(self, conn: Callable[..., sqlite3.Connection]):
        self.connect = conn

    def init_table(self):
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS attendance_detail (
                    id TEXT PRIMARY KEY NOT NULL,
                    absent_count INTEGER NOT NULL,
                    absent_with_permission INTEGER NOT NULL,
                    present_count INTEGER NOT NULL,
                    late_count INTEGER NOT NULL,
                    student_id TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES student(id)
                )
                """
            )
            conn.commit()

    def create(self, attendance_detail: AttendanceDetail):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO attendance_detail (id, absent_count, absent_with_permission, present_count, late_count, student_id) 
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    attendance_detail.id,
                    attendance_detail.absent_count,
                    attendance_detail.absent_with_permission,
                    attendance_detail.present_count,
                    attendance_detail.late_count,
                    attendance_detail.student_id,
                ),
            )
            conn.commit()

    def get(self, id: str):
        with self.connect() as conn:
            single_res = conn.execute(
                "SELECT * FROM attendance_detail WHERE id = ?", (id,)
            )
            row = single_res.fetchone()
            print("rowww", row)
            if row:
                result = AttendanceDetail(
                    id=row[0],
                    absent_count=row[1],
                    absent_with_permission=row[2],
                    present_count=row[3],
                    late_count=row[4],
                    student_id=row[5],
                )
                return result
            return None

    def update(self, id: str, modified: AttendanceDetailModifiable):
        old = self.get(id)
        if old is None:
            raise Exception("AttendanceDetail not found")

        updated = update_attendance_detail(old, modified)
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE attendance_detail
                SET absent_count = ?, absent_with_permission = ?, present_count = ?, late_count = ?
                WHERE id = ?
                """,
                (
                    updated.absent_count,
                    updated.absent_with_permission,
                    updated.present_count,
                    updated.late_count,
                    updated.id,
                ),
            )
            conn.commit()

    def delete(self, id: str):
        with self.connect() as conn:
            exec = conn.execute("DELETE FROM attendance_detail WHERE id = ?", (id,))
            conn.commit()
            return exec.rowcount

    def list(self) -> list[AttendanceDetail]:
        with self.connect() as conn:
            raw_list = conn.execute("SELECT * FROM attendance_detail")
            rows = raw_list.fetchall()
            result = []

            for row in rows:
                result.append(
                    AttendanceDetail(
                        id=row[0],
                        absent_count=row[1],
                        absent_with_permission=row[2],
                        present_count=row[3],
                        late_count=row[4],
                        student_id=row[5],
                    )
                )
            return result

    def get_by_student_id(self, student_id: str) -> Optional[AttendanceDetail]:
        with self.connect() as conn:
            single_res = conn.execute(
                "SELECT * FROM attendance_detail WHERE student_id = ?", (student_id,)
            )

            row = single_res.fetchone()
            print("DUMA", row)
            if row:
                result = AttendanceDetail(
                    id=row[0],
                    absent_count=row[1],
                    absent_with_permission=row[2],
                    present_count=row[3],
                    late_count=row[4],
                    student_id=row[5],
                )
                return result
            return None

    def mark_permission(self, student_id: str):
        attendance = self.get_by_student_id(student_id)
        if attendance is None:
            raise Exception("AttendanceDetail not found for the given student_id")

        with self.connect() as conn:
            conn.execute(
                """
                UPDATE attendance_detail
                SET absent_count = absent_count - 1,
                    absent_with_permission = absent_with_permission + 1
                WHERE student_id = ? AND absent_count > 0
                """,
                (student_id,),
            )
            conn.commit()
        return True

    def consolidate(self, attd_id: str, punctuality: Punctuality):

        with self.connect() as conn:
            fetcher = conn.execute(
                """
                SELECT s.id FROM attendance a
                JOIN enrollment e ON e.id = a.enrollment_id
                JOIN student s ON s.id = e.student_id
                WHERE a.id = ?
                """,
                (attd_id,),
            )

            student_id = fetcher.fetchone()[0]
            print("SSS", student_id)
            if punctuality == Punctuality.LATE:
                conn.execute(
                    """
                    UPDATE attendance_detail
                    SET late_count = late_count + 1
                    WHERE student_id = ?
                    """,
                    (student_id,),
                )
            elif punctuality == Punctuality.ONTIME:
                conn.execute(
                    """
                    UPDATE attendance_detail
                    SET present_count = present_count + 1
                    WHERE student_id = ?
                    """,
                    (student_id,),
                )
            elif punctuality == Punctuality.ABSENT:
                conn.execute(
                    """
                    UPDATE attendance_detail
                    SET absent_count = absent_count + 1
                    WHERE student_id = ?
                    """,
                    (student_id,),
                )
            elif punctuality == Punctuality.AUTO:
                # Implement your logic for AUTO here
                # For example, you might want to increment absent_count
                conn.execute(
                    """
                    UPDATE attendance_detail
                    SET absent_count = absent_count + 1
                    WHERE student_id = ?
                    """,
                    (student_id,),
                )
            conn.commit()
