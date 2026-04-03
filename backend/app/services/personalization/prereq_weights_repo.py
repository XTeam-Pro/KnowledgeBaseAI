from __future__ import annotations

from typing import Dict, Iterable, Tuple

import psycopg2

from app.config.settings import settings


def get_personal_prereq_weight_factors(
    user_uid: str | None,
    topic_uids: Iterable[str],
    tenant_id: str | None = None,
) -> Dict[Tuple[str, str], float]:
    """
    Returns per-user prereq weight multipliers from Postgres.

    Mapping key: (topic_uid, prereq_uid) -> factor.
    If DB/table is unavailable, returns empty mapping (caller should fallback to factor=1.0).
    """
    if not user_uid:
        return {}

    uids = [u for u in topic_uids if u]
    if not uids:
        return {}

    dsn = str(settings.pg_dsn) if settings.pg_dsn else ""
    if not dsn:
        return {}

    resolved_tenant = tenant_id or "default"
    factors: Dict[Tuple[str, str], float] = {}

    try:
        conn = psycopg2.connect(dsn)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT topic_uid, prereq_uid, weight_factor
                    FROM personal_prereq_weights
                    WHERE tenant_id = %s
                      AND user_uid = %s
                      AND topic_uid = ANY(%s)
                    """,
                    (resolved_tenant, user_uid, uids),
                )
                for topic_uid, prereq_uid, weight_factor in cur.fetchall():
                    try:
                        factor = float(weight_factor)
                    except (TypeError, ValueError):
                        factor = 1.0
                    # Allow suppressing influence with 0.0, but guard from negatives.
                    factors[(str(topic_uid), str(prereq_uid))] = max(0.0, factor)
        conn.close()
    except Exception:
        return {}

    return factors

