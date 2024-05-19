from fastapi import APIRouter, Depends

from src.model.enrollments import Enrollment, create_enrollment
from src.model.student import Student, create_stud
from src.response import ErrorTemplate, ResponseTemplate
from src.route.providers.base import get_enrollment_db, get_student_db
from src.schema.student import CreateStudent, EnrollStudent

student_router = APIRouter()


@student_router.get("/", response_model=ResponseTemplate[list[Student]])
def list_student_names(service=Depends(get_student_db)):
    res = service.list()
    return ResponseTemplate(res, "successfully retrieved students").to_json()


@student_router.post("/", response_model=ResponseTemplate[list[Student]])
def register_student(
    student_list: list[CreateStudent], service=Depends(get_student_db)
):
    students = []
    for student_data in student_list:
        students.append(create_stud(**student_data.model_dump()))

    res = service.create_many(students)
    return ResponseTemplate(res, "successfully register students").to_json()


@student_router.get("/{id}", response_model=ResponseTemplate[Student])
def get_student(id: str, service=Depends(get_student_db)):
    res = service.get(id)
    if res is None:
        return ErrorTemplate(
            "No student with this id found {}".format(id), "Retrieval error"
        ).to_json()

    return ResponseTemplate(
        res,
        "successfully retrieved student with id {}".format(id),
    ).to_json()


# @student_router.get("/enrollment/{id}", response_model=ResponseTemplate[Student])
# def get_student_enrollment(
#     id: str, service=Depends(get_student_db), enrollment_db=Depends(get_enrollment_db)
# ):
#     res = service.get(id)
#     if res is None:
#         return ErrorTemplate(
#             "No student with this id found {}".format(id), "Retrieval error"
#         ).to_json()

#     enrollment = enrollment_db.get_by_student(res.id)
#     return ResponseTemplate(
#         enrollment,
#         "successfully retrieved student enrollment with id {}".format(id),
#     ).to_json()


@student_router.post("/enrollment", response_model=ResponseTemplate[EnrollStudent])
def enroll_student(
    enroll: EnrollStudent,
    service=Depends(get_student_db),
    enrollment_db=Depends(get_enrollment_db),
):
    res = service.get(enroll.student_id)
    if res is None:
        return ErrorTemplate(
            "No student with this id found {}".format(enroll.student_id),
            "Retrieval error",
        ).to_json()

    enrollment = enrollment_db.create(create_enrollment(**enroll.model_dump()))
    return ResponseTemplate(
        enrollment,
        "successfully enroll student with id {}".format(enroll.student_id),
    ).to_json()


@student_router.get(
    "/enrollment/{enroll_id}", response_model=ResponseTemplate[EnrollStudent]
)
def get_enroll_student_info(
    enroll_id: str,
    enrollment_db=Depends(get_enrollment_db),
):
    res = enrollment_db.get_join_by_enrollment_id(enroll_id)
    # print("rr", res)
    if res is None:
        return ErrorTemplate(
            "No enrollment with this id found {}".format(enroll_id), "Retrieval error"
        ).to_json()

    return ResponseTemplate(
        res,
        "Result of enrollment with id {}".format(enroll_id),
    ).to_json()
