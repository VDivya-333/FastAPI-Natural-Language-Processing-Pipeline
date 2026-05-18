from fastapi import APIRouter

from app.schemas.request_schema import TextRequest
from app.services.nlp_service import sentiment_analysis


router = APIRouter()


@router.post("/sentiment")
async def sentiment(request: TextRequest):

    result = sentiment_analysis(request.text)

    return {
        "status": "success",
        "result": result
    }