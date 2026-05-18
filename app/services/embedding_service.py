from openai import OpenAI

from app.core.config import settings
from app.core.constants import EMBEDDING_MODEL


client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=f"{settings.OPENAI_BASE_URL}/embed"
)


def create_embedding(text: str):

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding