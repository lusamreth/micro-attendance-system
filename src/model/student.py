import sqlite3
import uuid
from collections.abc import Callable
from typing import List, Optional, Union

from pydantic import BaseModel

from src.model.attendance_detail import AttendanceDetail
from src.model.enrollments import Enrollment

# from src.model.enrollments import Enrollment, EnrollmentDBHandler
# from src.model.utils import check_constraints


class Student(BaseModel):
    id: str
    firstname: str
    lastname: Optional[str] = None
    generation: int
    gender: str
    major: Optional[str] = None
    phone_num: Optional[str] = None
    address: Optional[str] = None


class StudentAttendanceEnrollment(BaseModel):
    student: Student
    attendance: Optional[AttendanceDetail]
    enrollments: Union[list[str], list[Enrollment]]


def create_stud(
    firstname: str,
    lastname: str,
    generation: int,
    gender: str,
    major=None,
    phone_num=None,
    address=None,
) -> Student:
    stud_id = str(uuid.uuid4())
    return Student(
        id=stud_id,
        firstname=firstname,
        lastname=lastname,
        generation=generation,
        gender=gender,
        phone_num=phone_num,
        address=address,
        major=major,
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
                        gender TEXT NOT NULL,
                        major TEXT NULL
                    )
                """
            )
            conn.commit()

    def create(self, student: Student):
        with self.connect() as conn:
            conn.execute(
                """
                    INSERT INTO student (id, firstname, lastname, generation,
                                         gender, major) 
                    VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    student.id,
                    student.firstname,
                    "" if student.lastname is None else None,
                    student.generation,
                    student.gender,
                    student.major or "",
                ),
            )
            conn.commit()

    def get_by_name(self, fullname: str):
        with self.connect() as conn:
            splt = fullname.split(" ")
            firstname = splt[0]

            with self.connect() as conn:
                single_res = None
                if len(splt) < 2:
                    single_res = conn.execute(
                        "SELECT * FROM student WHERE firstname = ?",
                        (firstname.lower(),),
                    )
                else:
                    lastname = splt[1]
                    single_res = conn.execute(
                        "SELECT * FROM student WHERE firstname = ? AND lastname = ?",
                        (firstname.lower(), lastname.lower()),
                    )

                row = single_res.fetchone()
                if row:
                    result = Student(
                        id=row[0],
                        firstname=row[1],
                        lastname=row[2],
                        generation=row[3],
                        gender=row[4],
                        major=row[5] or "",
                    )
                    return result

                return None

    # def get_all_by_class(self,class_id:str):
    #     with self.connect() as conn:
    #         firstname, lastname = fullname.split(" ")
    #         with self.connect() as conn:
    #             single_res = conn.execute(
    #                 """
    #                 SELECT * FROM student s
    #                 JOIN classroom c on WHERE firstname = ? AND lastname = ?
    #                 """,
    #                 (firstname, lastname),
    #             )
    #             row = single_res.fetchone()
    #             if row:
    #                 result = Student(
    #                     id=row[0],
    #                     firstname=row[1],
    #                     lastname=row[2],
    #                     generation=row[3],
    #                     gender=row[4],
    #                     major=row[5] or "",
    #                 )
    #                 return result
    #             return None

    def create_many(self, student_list: list[Student]):
        with self.connect() as conn:
            for student in student_list:
                conn.execute(
                    """
                        INSERT INTO student (id, firstname, lastname,
                                             generation, gender, major) 
                        VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        student.id,
                        student.firstname,
                        "" if student.lastname is None else student.lastname.lower(),
                        student.generation,
                        student.gender,
                        student.major,
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

    def get(self, id: str, full_enrollment: bool = True):
        with self.connect() as conn:
            # Join student and attendance_detail tables
            query = """
            SELECT s.*, ad.*
            FROM student s
            LEFT JOIN attendance_detail ad ON s.id = ad.student_id
            WHERE s.id == ?
            """

            result = conn.execute(query, (id,))
            row = result.fetchone()

            student = Student(
                id=row[0],
                firstname=row[1],
                lastname=row[2],
                generation=row[3],
                gender=row[4],
                major=row[5],
            )

            attendance = (
                AttendanceDetail(
                    id=row[6],
                    absent_count=row[7],
                    absent_with_permission=row[8],
                    present_count=row[9],
                    late_count=row[10],
                    student_id=row[11],
                )
                if row[6]
                else None
            )

            # Fetch enrollments
            if full_enrollment:
                enrollment_query = """
                SELECT c.subject_name, c.lecturer_name, c.duration FROM enrollment e
                JOIN classroom c ON e.class_id = c.id
                WHERE student_id = ?
                """
                cursor = conn.execute(enrollment_query, (student.id,))
                print(cursor.fetchall())
                enrollments = [
                    Enrollment(id=e_row[0], class_id=e_row[1], student_id=e_row[2])
                    for e_row in cursor.fetchall()
                ]
                return StudentAttendanceEnrollment(
                    student=student, attendance=attendance, enrollments=enrollments
                )
            else:
                enrollment_query = """
                SELECT c.subject_name FROM enrollment e
                JOIN classroom c ON e.class_id = c.id
                WHERE student_id = ?
                """
                enrollments = [
                    e_row[0] for e_row in conn.execute(enrollment_query, (student.id,))
                ]

                return StudentAttendanceEnrollment(
                    student=student, attendance=attendance, enrollments=enrollments
                )

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

    def list_student_attendance_enrollment(
        self, full_enrollment: bool = False
    ) -> List[StudentAttendanceEnrollment]:
        with self.connect() as conn:
            # Join student and attendance_detail tables
            query = """
            SELECT s.*, ad.*
            FROM student s
            LEFT JOIN attendance_detail ad ON s.id = ad.student_id
            """
            result = conn.execute(query)
            rows = result.fetchall()

            student_data = []
            for row in rows:
                student = Student(
                    id=row[0],
                    firstname=row[1],
                    lastname=row[2],
                    generation=row[3],
                    gender=row[4],
                    major=row[5],
                )
                attendance = (
                    AttendanceDetail(
                        id=row[6],
                        absent_count=row[7],
                        absent_with_permission=row[8],
                        present_count=row[9],
                        late_count=row[10],
                        student_id=row[11],
                    )
                    if row[6]
                    else None
                )

                # Fetch enrollments
                if full_enrollment:
                    enrollment_query = """
                    SELECT c.subject_name, c.lecturer_name, c.duration FROM enrollment e
                    JOIN classroom c ON e.class_id = c.id
                    WHERE student_id = ?
                    """
                    enrollments = [
                        Enrollment(id=e_row[0], class_id=e_row[1], student_id=e_row[2])
                        for e_row in conn.execute(enrollment_query, (student.id,))
                    ]
                else:
                    enrollment_query = """
                    SELECT c.subject_name FROM enrollment e
                    JOIN classroom c ON e.class_id = c.id
                    WHERE student_id = ?
                    """
                    enrollments = [
                        e_row[0]
                        for e_row in conn.execute(enrollment_query, (student.id,))
                    ]
                print("ENC", enrollments)
                student_data.append(
                    StudentAttendanceEnrollment(
                        student=student, attendance=attendance, enrollments=enrollments
                    )
                )

            return student_data
