from fastapi import APIRouter, Query, status, Response

from app.agent.Agent import get_agent

from app.models.api_models import APIChatResponse, ErrorResponse
from app.models.chat_models import InChatRequest

chat_router = APIRouter(prefix="/chat", tags=["chat"])

@chat_router.post("", response_model=APIChatResponse, status_code=status.HTTP_200_OK)
def chat(request: InChatRequest, response: Response):

    try:
        agent = get_agent()
        state = agent.chat(request.in_message)
        response.status_code = status.HTTP_200_OK
        return APIChatResponse(data=state,
                               message="Answer generated successfully",
                               error=None)

    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIChatResponse(data={},
                           message="Chatting failed, something went wrong.",
                           error=ErrorResponse(error_code=status.HTTP_400_BAD_REQUEST,
                                               error_message=str(e)))