from groq import AsyncGroq
from config import settings

_client = None

def get_groq() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _client

async def chat_complete(
    system: str,
    user: str,
    model: str = "llama-3.1-8b-instant",
    max_tokens: int = 512
) -> str:
    client = get_groq()
    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        max_tokens=max_tokens
    )
    return resp.choices[0].message.content.strip()
