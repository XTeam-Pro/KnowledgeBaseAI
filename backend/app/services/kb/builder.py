from __future__ import annotations

from typing import Any

from app.config.settings import settings


async def openai_chat_async(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    model: str = "gpt-4o-mini",
    **kwargs: Any,
) -> dict[str, Any]:
    """Async OpenAI chat wrapper used by legacy KB services.

    Returns:
      {"ok": True, "content": "..."} on success
      {"ok": False, "error": "..."} on failure
    """
    api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else ""
    if not api_key:
        return {"ok": False, "error": "OPENAI_API_KEY is not configured"}

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        content = (resp.choices[0].message.content or "").strip()
        return {"ok": True, "content": content}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

