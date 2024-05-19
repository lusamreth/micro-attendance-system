import sqlite3
import uuid
from collections.abc import Callable

from pydantic import BaseModel

# from src.model.enrollments import Enrollment, EnrollmentDBHandler
# from src.model.utils import check_constraints


class Student(BaseModel):
    id: str
    firstname: str
    lastname: str
    generation: int
    gender: str


def create_stud(firstname: str, lastname: str, generation: int, gender: str) -> Student:
    stud_id = str(uuid.uuid4())
    return Student(
        id=stud_id,
        firstname=firstname,
        lastname=lastname,
        generation=generation,
        gender=gender,
    )


class StudentModifiable(BaseModel):
    generation: int
    pass


def update_stud(old: Student, modified: StudentModifiable) -> Student:
    return Student(
        id=old.id,
        firstname=old.firstname,
        lastname=old.lastname,
        generation=modified.generation,
        gender=old.gender,
    )


class StudentDBHandler:
    def __init__(self, conn: Callable[..., sqlite3.Connection]):
        self.connect = conn
        # self.enrollmentHandler = EnrollmentDBHandler(conn)

    def init_table(self):
        with self.connect() as conn:
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS student (
                        id TEXT PRIMARY KEY NOT NULL,
                        firstname TEXT NOT NULL,
                        lastname TEXT NOT NULL,
                        generation INTEGER NOT NULL,
                        gender TEXT NOT NULL
                    )
                """
            )
            conn.commit()

    def create(self, student: Student):
        with self.connect() as conn:
            conn.execute(
                """
                    INSERT INTO student (id, firstname, lastname, generation, gender) 
                    VALUES (?, ?, ?, ?, ?);
                """,
                (
                    student.id,
                    student.firstname,
                    student.lastname,
                    student.generation,
                    student.gender,
                ),
            )
            conn.commit()

    def get_by_name(self, fullname: str):
        with self.connect() as conn:
            firstname, lastname = fullname.split(" ")
            with self.connect() as conn:
                single_res = conn.execute(
                    "SELECT * FROM student WHERE firstname = ? AND lastname = ?",
                    (firstname, lastname),
                )
                row = single_res.fetchone()
                if row:
                    result = Student(
                        id=row[0],
                        firstname=row[1],
                        lastname=row[2],
                        generation=row[3],
                        gender=row[4],
                    )
                    return result
                return None

    def create_many(self, student_list: list[Student]):
        with self.connect() as conn:
            for student in student_list:
                conn.execute(
                    """
                        INSERT INTO student (id, firstname, lastname, generation, gender) 
                        VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        student.id,
                        student.firstname,
                        student.lastname,
                        student.generation,
                        student.gender,
                    ),
                )
                conn.commit()
                # Enrollment handling
                # Assuming you have a function to get classroom id or pass it along with student creation
                # self.enrollmentHandler.create(
                #     Enrollment(class_id=class_id, student_id=student.id)
                # )
            return student_list

    def update(self, id: str, modified: StudentModifiable):
        old = self.get(id)
        if old is None:
            raise Exception("Student not found")

        updated = update_stud(old, modified)
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE student
                SET generation = ?
                WHERE id = ?
                """,
                (updated.generation, updated.id),
            )
            conn.commit()

    def delete(self, id: str):
        with self.connect() as conn:
            exec = conn.execute("DELETE FROM student WHERE id = ?", (id,))
            conn.commit()
            return exec.rowcount

    def get(self, id: str):
        # print("IDD",id)
        with self.connect() as conn:
            single_res = conn.execute("SELECT * FROM student WHERE id = ?", (id,))
            row = single_res.fetchone()
            if row:
                result = Student(
                    id=row[0],
                    firstname=row[1],
                    lastname=row[2],
                    generation=row[3],
                    gender=row[4],
                )
                return result
            return None

    def list(self) -> list[Student]:
        with self.connect() as conn:
            raw_list = conn.execute("SELECT * FROM student")
            rows = raw_list.fetchall()
            result = []

            for row in rows:
                result.append(
                    Student(
                        id=row[0],
                        firstname=row[1],
                        lastname=row[2],
                        generation=row[3],
                        gender=row[4],
                    )
                )
            return result
