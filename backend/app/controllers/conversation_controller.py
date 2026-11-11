import asyncio
import json
import logging
import uuid
import sqlite3
from collections.abc import AsyncIterator


from src.btc.config import DB_PATH

from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse

from app.models import message
from app.services import chat_service


logger = logging.getLogger(__name__)


def create_conversation() -> dict:
    try:
        return chat_service.create_conversation()
    except Exception as exc:
        logger.exception("Could not create a conversation")
        raise HTTPException(status_code=500, detail="Something went wrong") from exc


def list_conversations() -> list[dict]:
    try:
        return chat_service.list_conversations()
    except Exception as exc:
        logger.exception("Could not list conversations")
        raise HTTPException(status_code=500, detail="Something went wrong") from exc


def get_conversation(conversation_id: str) -> dict:
    try:
        result = chat_service.get_conversation(conversation_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Could not load conversation %s", conversation_id)
        raise HTTPException(status_code=500, detail="Something went wrong") from exc


async def send_message(
    conversation_id: str,
    request: Request,
) -> StreamingResponse:
    try:
        payload = await request.json()
        incoming = payload.get("messages", [])
        latest_message = incoming[-1] if incoming else {}
        question = message_text(latest_message).strip()
        thread_id = payload.get("threadId") or conversation_id
        run_id = payload.get("runId") or str(uuid.uuid4())
    except Exception as exc:
        logger.exception("Could not read chat request for conversation %s", conversation_id)
        raise HTTPException(status_code=400, detail="Invalid chat request") from exc

    if not question:
        raise HTTPException(status_code=422, detail="Message cannot be empty")
    if chat_service.get_conversation(conversation_id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found")


    conn = sqlite3.connect(DB_PATH)
    try:

        message.create(conversation_id, "user", question)
        answer = chat_service.answer_question(conn, question)
        # answer = """
        #
        #     Glycerin (also called glycerol) is a humectant, meaning it pulls water into the skin. It's one of the most common and best-tolerated ingredients in skincare, haircare, and cosmetics.
        #
        #     **What it does**
        #     - Draws moisture from the air and the deeper skin layers into the outer layer, keeping skin hydrated
        #     - Softens and smooths skin texture
        #     - Supports the skin barrier, helping reduce water loss
        #     - Helps other ingredients feel less heavy and improves spreadability in formulas
        #
        #     **Where it's found**
        #     Moisturizers, serums, cleansers, soaps, lip balms, shampoos and conditioners, toothpaste, and many DIY recipes.
        #
        #     **Who it suits**
        #     Nearly everyone, including dry, sensitive, and acne-prone skin. It's non-comedogenic and rarely irritating. Allergic reactions are uncommon.
        #
        #     **Things to know**
        #     - **Concentration matters.** Most products use 3 to 10%. Very high concentrations (above roughly 30%) can feel sticky and may draw water out of skin in very dry air.
        #     - **Dry climates.** In low humidity, a humectant works best when sealed in with an occlusive or moisturizer on top, otherwise it can pull water from deeper skin instead of the air.
        #     - **Source.** It can be plant-derived (palm, coconut, soy), animal-derived, or synthetic. Vegetable glycerin is the usual choice for vegan products.
        #     - **Hair.** It adds moisture in humid conditions but can cause frizz or stiffness in very dry or very humid extremes, depending on hair type.
        #
        #     **Simple use**
        #     Apply on damp skin, then follow with a moisturizer. For DIY, dilute it (for example, a few drops in a water-based toner or lotion) rather than using it neat.
        #     """

        saved_answer = message.create(conversation_id, "assistant", answer)
    except Exception as exc:
        logger.exception("Could not answer question for conversation %s", conversation_id)
        raise HTTPException(status_code=500, detail="Something went wrong") from exc
    finally:
        conn.close()

    assistant_message_id = str(saved_answer.get("id") or uuid.uuid4())

    async def events() -> AsyncIterator[str]:
        chunks = (
            {"type": "RUN_STARTED", "threadId": thread_id, "runId": run_id},
            {"type": "TEXT_MESSAGE_START", "messageId": assistant_message_id, "role": "assistant"},
        )
        for event in chunks:
            yield f"data: {json.dumps(event)}\n\n"

        # The current answer provider returns a complete string. The SSE
        # transport still delivers it incrementally, and can consume a true
        # token iterator when the provider exposes one.
        for offset in range(0, len(answer), 24):
            event = {
                "type": "TEXT_MESSAGE_CONTENT",
                "messageId": assistant_message_id,
                "delta": answer[offset : offset + 24],
            }
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.012)

        for event in (
            {"type": "TEXT_MESSAGE_END", "messageId": assistant_message_id},
            {"type": "RUN_FINISHED", "threadId": thread_id, "runId": run_id},
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def message_text(message_data: dict) -> str:
    content = message_data.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") in {"text", "input_text"}
        )
    parts = message_data.get("parts", [])
    return "".join(
        part.get("content", "")
        for part in parts
        if isinstance(part, dict) and part.get("type") == "text"
    )
