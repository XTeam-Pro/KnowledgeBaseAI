"""Lightweight telemetry publisher for KnowledgeBaseAI.

Publishes events to Redis list ``telemetry:kb_events`` as JSON.
The StudyNinja-API telemetry worker drains this list and writes to ClickHouse.

All calls are fire-and-forget — failures are logged but never block the caller.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.config.settings import settings
from app.events.publisher import get_redis

logger = logging.getLogger(__name__)

TELEMETRY_REDIS_KEY = "telemetry:kb_events"


def track_event(
    event_type: str,
    payload: dict[str, Any] | None = None,
    *,
    user_id: str | None = None,
    correlation_id: str | None = None,
) -> None:
    """Publish a telemetry event to Redis (fire-and-forget)."""
    try:
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id or "",
            "service": "knowledgebase-ai",
            "env": settings.app_env.value,
            "correlation_id": correlation_id or "",
            "payload": payload or {},
        }
        r = get_redis()
        r.lpush(TELEMETRY_REDIS_KEY, json.dumps(event, ensure_ascii=False))
    except Exception:
        logger.debug("Telemetry publish failed", exc_info=True)
