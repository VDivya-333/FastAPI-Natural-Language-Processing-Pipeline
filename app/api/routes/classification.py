from fastapi import APIRouter

from app.schemas.request_schema import TextRequest
from app.services.nlp_service import classify_text


router = APIRouter()


@router.post("/classify")
async def classify(request: TextRequest):

    result = classify_text(request.text)

    return {
        "status": "success",
        "result": result
    }