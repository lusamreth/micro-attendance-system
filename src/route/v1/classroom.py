from fastapi import APIRouter, Depends

from src.model.classroom import Classroom, create_classroom
from src.response import ErrorTemplate, ResponseTemplate
from src.route.providers.base import get_classroom_db
from src.schema.classroom import CreateClassroom

classroom_router = APIRouter()


@classroom_router.get("/", response_model=ResponseTemplate[list[Classroom]])
def list_classroom_names(service=Depends(get_classroom_db)):
    res = service.list()
    return ResponseTemplate(res, "Successfully retrieved classrooms").to_json()


@classroom_router.post("/", response_model=ResponseTemplate[list[Classroom]])
def register_classroom(
    classroom_list: list[CreateClassroom], service=Depends(get_classroom_db)
):
    classrooms = []
    for classroom_data in classroom_list:
        classrooms.append(create_classroom(**classroom_data.model_dump()))

    res = service.create_many(classrooms)
    return ResponseTemplate(res, "Successfully registered classrooms").to_json()


@classroom_router.get("/{id}", response_model=ResponseTemplate[Classroom])
def get_classroom(id: str, service=Depends(get_classroom_db)):
    res = service.get(id)
    if res is None:
        return ErrorTemplate(
            "No classroom with this id found {}".format(id), "Retrieval error"
        ).to_json()

    return ResponseTemplate(
        res,
        "Successfully retrieved classroom with id {}".format(id),
    ).to_json()
