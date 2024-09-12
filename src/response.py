from typing import Generic, TypeVar, Union

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseTemplate(GenericModel, Generic[T]):
    message: str
    data: Union[T, list[T]]  # Allow both single object and list of objects
    status_code: int

    def __init__(self, data: Union[T, list[T]], msg: str, status_code=200):
        super().__init__(message=msg, data=data, status_code=status_code)
        self.message = msg
        self.data = data
        self.status_code = status_code

    def to_json(self):
        return JSONResponse(
            content={"message": self.message, "data": self._prepare_data(self.data)},
            status_code=self.status_code,
        )

    def _prepare_data(self, data: Union[T, list[T]]):
        # Check if data is a list and process accordingly
        if isinstance(data, list):
            return [
                item.model_dump() if isinstance(item, BaseModel) else item
                for item in data
            ]
        # If it's a single object and is a BaseModel, return its dictionary
        if isinstance(data, BaseModel):
            return data.model_dump()
        # If it's not a list or BaseModel, return the data as is
        return data


class ErrorTemplate(GenericModel, Generic[T]):
    message: str
    errors: Union[T, list[T]]  # Allow both single object and list of objects
    status_code: int

    def __init__(self, errors: Union[T, list[T]], msg: str, status_code=400):
        super().__init__(message=msg, errors=errors, status_code=status_code)
        self.message = msg
        self.errors = errors
        self.status_code = status_code

    def to_json(self):
        return JSONResponse(
            content={"message": self.message, "data": self._prepare_data(self.errors)},
            status_code=self.status_code,
        )

    def _prepare_data(self, errors: Union[T, list[T]]):
        # Check if errors is a list and process accordingly
        if isinstance(errors, list):
            return [
                item.model_dump() if isinstance(item, BaseModel) else item
                for item in errors
            ]
        # If it's a single object and is a BaseModel, return its dictionary
        if isinstance(errors, BaseModel):
            return errors.model_dump()
        # If it's not a list or BaseModel, return the errors as is
        return errors
