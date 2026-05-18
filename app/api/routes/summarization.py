from fastapi import APIRouter

from app.schemas.request_schema import TextRequest
from app.services.nlp_service import summarize_text


router = APIRouter()


@router.post("/summarize")
async def summarize(request: TextRequest):

    result = summarize_text(request.text)

    return {
        "status": "success",
        "result": result
    }