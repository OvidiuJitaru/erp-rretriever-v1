from typing import Any, Optional

from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error_code: int
    error_message: str

class APIChatResponse(BaseModel):
    data: Any
    message: str
    error: Optional[ErrorResponse]