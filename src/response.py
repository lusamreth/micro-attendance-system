from typing import Generic, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseTemplate(GenericModel, Generic[T]):
    message: str
    data: T
    status_code: int

    def __init__(self, data, msg, status_code=200):
        super().__init__(message=msg, data=data, status_code=status_code)
        self.message = msg
        self.data = data
        self.status_code = status_code

    def to_json(self):
        if isinstance(self.data, list):
            _list_dict = []
            for data in self.data:
                print(type(data))
                if isinstance(data, BaseModel):
                    _list_dict.append(data.model_dump())

            return JSONResponse(
                content={"message": self.message, "data": _list_dict},
                status_code=self.status_code,
            )

        if isinstance(self.data, BaseModel):
            return JSONResponse(
                content={"message": self.message, "data": self.data.model_dump()},
                status_code=self.status_code,
            )
        else:
            JSONResponse(
                content={"message": self.message, "data": self.data},
                status_code=self.status_code,
            )

        return JSONResponse({}, status_code=self.status_code)


class ErrorTemplate(GenericModel, Generic[T]):
    message: str
    errors: T
    status_code: int

    def __init__(self, errors, msg, status_code=400):
        super().__init__(message=msg, errors=errors, status_code=status_code)
        self.message = msg
        self.errors = errors
        self.status_code = status_code

    def to_json(self):
        if isinstance(self.errors, list):
            _list_dict = []
            for data in self.errors:
                print(type(data))
                if isinstance(data, BaseModel):
                    _list_dict.append(data.model_dump())

            return JSONResponse(
                content={"message": self.message, "data": _list_dict},
                status_code=self.status_code,
            )
        if isinstance(self.errors, BaseModel):
            return JSONResponse(
                content={"message": self.message, "data": self.errors.model_dump()},
                status_code=self.status_code,
            )
        else:
            return JSONResponse(
                content={"message": self.message, "data": self.errors},
                status_code=self.status_code,
            )
