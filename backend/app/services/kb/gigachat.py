"""GigaChat async client — drop-in replacement for openai_chat_async().

Usage:
    from app.services.kb.gigachat import gigachat_chat_async
    res = await gigachat_chat_async(messages, temperature=0.9)
    # Returns {"ok": True, "content": "..."} or {"ok": False, "error": "..."}

Token lifecycle: GigaChat OAuth tokens live ~30 min. A singleton token is cached
in-process and refreshed automatically 60 s before expiry.
"""

import time
import uuid as _uuid

import httpx

from app.config.settings import settings
from app.core.logging import logger

_GC_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
_GC_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
_GC_SCOPE = "GIGACHAT_API_PERS"

# Singleton token state
_token: str | None = None
_token_expires_at: float = 0.0


async def _get_token() -> str:
    global _token, _token_expires_at
    if _token and time.time() < _token_expires_at - 60:
        return _token

    creds = settings.gigachat_credentials
    if not creds:
        raise RuntimeError("GIGACHAT_CREDENTIALS is not set")

    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        resp = await client.post(
            _GC_AUTH_URL,
            headers={
                "Authorization": f"Basic {creds}",
                "RqUID": str(_uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"scope": _GC_SCOPE},
        )
        resp.raise_for_status()
        data = resp.json()

    _token = data["access_token"]
    _token_expires_at = data["expires_at"] / 1000  # ms → s
    return _token


async def gigachat_chat_async(
    messages: list,
    temperature: float = 0.7,
    model: str = "GigaChat",
    max_tokens: int = 600,
) -> dict:
    """Call GigaChat and return {"ok": True, "content": ...} or {"ok": False, "error": ...}."""
    try:
        token = await _get_token()
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            resp = await client.post(
                _GC_API_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return {"ok": True, "content": content}
    except Exception as exc:
        logger.warning("gigachat_error", error=str(exc))
        return {"ok": False, "error": str(exc)}
