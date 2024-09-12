# CREATE TABLE Enrollments (
#     student_id INT,
#     classroom_id INT,
#     FOREIGN KEY (student_id) REFERENCES Students(student_id),
#     FOREIGN KEY (classroom_id) REFERENCES Classrooms(classroom_id),
#     PRIMARY KEY (student_id, classroom_id)
# );

import sqlite3
import uuid
from collections.abc import Callable

from pydantic import BaseModel


class Enrollment(BaseModel):
    id: str
    class_id: str
    student_id: str


class EnrollmentJoinResult(BaseModel):
    enrollment_id: str
    student_id: str
    first_name: str
    last_name: str
    classroom_id: str
    lecturer_name: str
    duration: int
    lecture_time: float
    late_penalty_duration: float
    record_interval: float | None


def create_enrollment(class_id: str, student_id: str) -> Enrollment:
    return Enrollment(id=str(uuid.uuid4()), class_id=class_id, student_id=student_id)


class EnrollmentDBHandler:
    def __init__(self, conn: Callable[..., sqlite3.Connection]):
        self.connect = conn

    def init_table(self):
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS enrollment (
                    id TEXT NOT NULL,
                    class_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    FOREIGN KEY (class_id) REFERENCES classroom(id),
                    FOREIGN KEY (student_id) REFERENCES student(id),
                    PRIMARY KEY (id)
                )
                """
            )
            conn.commit()

    def create(self, enrollment: Enrollment):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO enrollment (id, class_id, student_id)
                VALUES (?, ?, ?)
                """,
                (enrollment.id, enrollment.class_id, enrollment.student_id),
            )
            conn.commit()
            return enrollment

    def create_many(self, enrollment_list: list[Enrollment]):
        with self.connect() as conn:
            for enrollment in enrollment_list:
                conn.execute(
                    """
                    INSERT INTO enrollment (id, class_id, student_id)
                    VALUES (?, ?, ?)
                    """,
                    (enrollment.id, enrollment.class_id, enrollment.student_id),
                )
            conn.commit()
            return enrollment_list

    def delete(self, class_id: str, student_id: str):
        with self.connect() as conn:
            exec = conn.execute(
                """
                DELETE FROM enrollment
                WHERE class_id = ? AND student_id = ?
                """,
                (class_id, student_id),
            )
            conn.commit()
            return exec.rowcount

    def get_by_class(self, class_id: str) -> list[Enrollment]:
        with self.connect() as conn:
            raw_list = conn.execute(
                """
                SELECT * FROM enrollment
                WHERE class_id = ?
                """,
                (class_id,),
            )
            rows = raw_list.fetchall()
            result = []
            for row in rows:
                result.append(Enrollment(id=row[0], class_id=row[1], student_id=row[2]))
            return result

    def get(self, en_id: str) -> Enrollment:
        with self.connect() as conn:
            raw_list = conn.execute(
                """
                SELECT * FROM enrollment
                WHERE id = ?
                """,
                (en_id,),
            )
            row = raw_list.fetchone()
            return Enrollment(id=row[0], class_id=row[1], student_id=row[2])

    def get_by_student(self, student_id: str) -> list[Enrollment]:
        print("stu", student_id)
        with self.connect() as conn:
            raw_list = conn.execute(
                """
                SELECT * FROM enrollment
                INNER JOIN student on student.id = student_id
                WHERE student_id = ?
                """,
                (student_id,),
            )
            rows = raw_list.fetchall()
            result = []
            for row in rows:
                result.append(Enrollment(id=row[0], class_id=row[1], student_id=row[2]))
            return result

    def list_enrollment(self) -> list[Enrollment]:
        with self.connect() as conn:
            raw_list = conn.execute("SELECT * FROM enrollment")
            rows = raw_list.fetchall()
            result = []
            for row in rows:
                result.append(Enrollment(id=row[0], class_id=row[1], student_id=row[2]))
            return result

    def list_enrollment_by_class(self, class_id) -> list[Enrollment]:
        with self.connect() as conn:
            raw_list = conn.execute(
                """
                SELECT * FROM enrollment e
                JOIN classroom c on c.id = e.id
                WHERE c.id == ?
                """,
                (class_id,),
            )
            rows = raw_list.fetchall()
            print(rows)
            result = []
            for row in rows:
                result.append(Enrollment(id=row[0], class_id=row[1], student_id=row[2]))
            return result

    def get_join_by_enrollment_id(
        self, enrollment_id: str
    ) -> list[EnrollmentJoinResult]:
        with self.connect() as conn:
            return get_join_by_enrollment_id_internal(conn, enrollment_id)


def get_join_by_enrollment_id_internal(
    conn, enrollment_id: str
) -> list[EnrollmentJoinResult]:
    raw_list = conn.execute(
        """
        SELECT e.id as enrollment_id, s.id as student_id, s.firstname as firstname, s.lastname as lastname,
               c.id as classroom_id, c.lecturer_name, c.duration, c.lecture_time,
               c.late_penalty_duration, c.record_interval
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        JOIN classroom c ON e.class_id = c.id
        WHERE e.id = ?
        """,
        # """
        # SELECT *
        # FROM enrollment e
        # JOIN student s ON e.student_id = s.id
        # JOIN classroom c ON e.class_id = c.id
        # WHERE e.id = ?
        # """,
        (enrollment_id,),
    )

    rows = raw_list.fetchall()
    result = []

    for row in rows:
        result.append(
            EnrollmentJoinResult(
                enrollment_id=row[0],
                student_id=row[1],
                first_name=row[2],
                last_name=row[3],
                classroom_id=row[4],
                lecturer_name=row[5],
                duration=row[6],
                lecture_time=row[7],
                late_penalty_duration=row[8],
                record_interval=row[9],
            )
        )
    return result
