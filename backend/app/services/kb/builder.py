from __future__ import annotations

import time
from typing import Any

from app.config.settings import settings

_RATE_LIMIT_COOLDOWN_UNTIL: float = 0.0
_DEFAULT_RATE_LIMIT_COOLDOWN_SEC: float = 4.0


def _is_rate_limited_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    if "429" in msg or "too many requests" in msg or "rate limit" in msg:
        return True
    return exc.__class__.__name__.lower() == "ratelimiterror"


def _extract_retry_after_seconds(exc: Exception) -> float:
    retry_after = None
    response = getattr(exc, "response", None)
    if response is not None:
        headers = getattr(response, "headers", None)
        if headers:
            retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after is not None:
        try:
            return max(float(retry_after), 0.0)
        except Exception:
            pass
    return _DEFAULT_RATE_LIMIT_COOLDOWN_SEC


async def openai_chat_async(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    model: str = "gpt-4o-mini",
    request_timeout: float = 20.0,
    max_retries: int = 0,
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

    global _RATE_LIMIT_COOLDOWN_UNTIL
    now = time.monotonic()
    if now < _RATE_LIMIT_COOLDOWN_UNTIL:
        return {
            "ok": False,
            "error": "OPENAI_RATE_LIMITED_COOLDOWN",
            "retry_after_seconds": round(_RATE_LIMIT_COOLDOWN_UNTIL - now, 3),
        }

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=api_key,
            max_retries=max_retries,
            timeout=request_timeout,
        )
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        content = (resp.choices[0].message.content or "").strip()
        _RATE_LIMIT_COOLDOWN_UNTIL = 0.0
        return {"ok": True, "content": content}
    except Exception as exc:
        if _is_rate_limited_error(exc):
            retry_after = _extract_retry_after_seconds(exc)
            _RATE_LIMIT_COOLDOWN_UNTIL = time.monotonic() + retry_after
            return {
                "ok": False,
                "error": "OPENAI_RATE_LIMITED",
                "retry_after_seconds": retry_after,
            }
        return {"ok": False, "error": str(exc)}
