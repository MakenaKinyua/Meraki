from fastapi import APIRouter, Request

from app.controllers import conversation_controller as controller
from app.schemas.chat import ConversationResponse, ConversationSummary


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=201)
def create_conversation():
    return controller.create_conversation()


@router.get("", response_model=list[ConversationSummary])
def list_conversations():
    return controller.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str):
    return controller.get_conversation(conversation_id)


@router.post("/{conversation_id}/messages")
async def send_message(conversation_id: str, request: Request):
    return await controller.send_message(conversation_id, request)
