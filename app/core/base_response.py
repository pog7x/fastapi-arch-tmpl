from typing import Any, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class BaseError(BaseModel):
    message: str
    detail: Optional[str] = None


class BaseResponse(GenericModel, Generic[T]):
    result: Optional[T] = None
    errors: Optional[List[Union[BaseError, dict]]] = []
    success: Optional[bool] = None

    def dict(self, *args: Any, **kwargs: Any) -> dict:
        d = super().dict(*args, **kwargs)
        d["success"] = not self.errors
        return d

    @classmethod
    def from_result(cls, result: T) -> "BaseResponse":
        return cls(result=result)

    @classmethod
    def from_error_str(
        cls, error: str = "", detail: Optional[str] = None
    ) -> "BaseResponse":
        return cls(errors=[BaseError(message=error, detail=detail)])
