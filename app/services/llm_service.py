from openai import OpenAI

from app.core.config import settings
from app.core.constants import MODEL_NAME


client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)


def generate_completion(prompt: str, json_mode: bool = False):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a specialized NLP assistant. You must output a single valid JSON object when requested. Do NOT wrap the result in a list or array unless specifically asked."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        response_format={"type": "json_object"} if json_mode else None
    )

    return response.choices[0].message.content