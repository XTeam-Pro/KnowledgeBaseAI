from __future__ import annotations

import time
from typing import Any

from app.config.settings import settings
from app.core.logging import logger

_RATE_LIMIT_COOLDOWN_UNTIL: float = 0.0
_DEFAULT_RATE_LIMIT_COOLDOWN_SEC: float = 4.0
_DEFAULT_MAX_TOKENS: int = 600
_MAX_TOKENS_CAP: int = 650
_FAST_MODEL: str = settings.fast_model

# Models that do not support custom temperature (only default=1 allowed)
_NO_TEMPERATURE_PREFIXES = ("gpt-5", "o1", "o3", "o4")


def _supports_temperature(model: str) -> bool:
    return not any(model.startswith(p) for p in _NO_TEMPERATURE_PREFIXES)


# Singleton client — created once per process, reused across all calls
_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import AsyncOpenAI
        api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else ""
        _openai_client = AsyncOpenAI(api_key=api_key, max_retries=0, timeout=20.0)
    return _openai_client


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
    model: str = _FAST_MODEL,
    feature: str = "unknown",
    max_tokens: int | None = None,
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
        client = _get_openai_client()
        model_to_use = model or _FAST_MODEL
        max_tokens_to_use = int(max_tokens or kwargs.pop("max_tokens", _DEFAULT_MAX_TOKENS))
        max_tokens_to_use = max(1, min(max_tokens_to_use, _MAX_TOKENS_CAP))
        call_kwargs: dict[str, Any] = {"max_completion_tokens": max_tokens_to_use, **kwargs}
        if _supports_temperature(model_to_use):
            call_kwargs["temperature"] = temperature
        resp = await client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            **call_kwargs,
        )
        content = (resp.choices[0].message.content or "").strip()
        usage_obj = getattr(resp, "usage", None)
        usage = {
            "prompt_tokens": int(getattr(usage_obj, "prompt_tokens", 0) or 0),
            "completion_tokens": int(getattr(usage_obj, "completion_tokens", 0) or 0),
            "total_tokens": int(getattr(usage_obj, "total_tokens", 0) or 0),
        }
        if not usage["total_tokens"]:
            usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        logger.info(
            "llm_usage",
            feature=feature,
            model=model_to_use,
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
        )
        _RATE_LIMIT_COOLDOWN_UNTIL = 0.0
        return {
            "ok": True,
            "content": content,
            "usage": usage,
            "model": model_to_use,
            "feature": feature,
        }
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
