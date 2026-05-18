from fastapi import APIRouter

from app.schemas.request_schema import TextRequest
from app.services.nlp_service import extract_entities


router = APIRouter()


@router.post("/entities")
async def entities(request: TextRequest):

    result = extract_entities(request.text)

    return {
        "status": "success",
        "result": result
    }