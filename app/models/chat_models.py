from pydantic import BaseModel


class InChatRequest(BaseModel):
    in_message: str