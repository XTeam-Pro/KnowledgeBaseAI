from typing import Dict, List
from app.services.graph.neo4j_repo import get_driver
from app.services.personalization.prereq_weights_repo import get_personal_prereq_weight_factors
from app.services.reasoning.prereq_scoring import (
    compute_topic_prereq_state,
    normalize_prereq_edges,
)


def compute_gaps(
    subject_uid: str,
    progress: Dict[str, float],
    goals: List[str] | None = None,
    prereq_threshold: float = 0.7,
    user_uid: str | None = None,
    tenant_id: str | None = None,
) -> Dict[str, List[Dict]]:
    drv = get_driver()
    blocking: List[Dict] = []
    latent: List[Dict] = []
    with drv.session() as s:
        rows = s.run(
            "MATCH (sub:Subject {uid:$su})-[:CONTAINS]->(:Section)-[:CONTAINS]->(t:Topic) "
            "WHERE ($tid IS NULL OR sub.tenant_id = $tid) "
            "AND ($tid IS NULL OR t.tenant_id = $tid) "
            "OPTIONAL MATCH (t)-[pr:PREREQ]->(pre:Topic) "
            "RETURN t.uid AS uid, t.title AS title, collect({uid: pre.uid, weight: coalesce(pr.weight, 0.5), is_hard: coalesce(pr.is_hard, false)}) AS prereqs",
            {"su": subject_uid, "tid": tenant_id},
        ).data()

        personal_factors = get_personal_prereq_weight_factors(
            user_uid=user_uid,
            topic_uids=[r.get("uid") for r in rows if r.get("uid")],
            tenant_id=tenant_id,
        )

        for r in rows:
            tuid = r["uid"]
            prereq_state = compute_topic_prereq_state(
                topic_uid=tuid,
                prereq_edges=normalize_prereq_edges(r.get("prereqs") or []),
                progress=progress,
                personal_factors=personal_factors,
                readiness_threshold=prereq_threshold,
                hard_threshold=0.5,
            )
            missing = list(
                dict.fromkeys(
                    prereq_state["blocking_prereqs"] + prereq_state["soft_missing_prereqs"]
                )
            )
            if not prereq_state["is_unlocked"]:
                blocking.append({
                    "topic_uid": tuid,
                    "why": "missing_prereqs",
                    "prereqs": missing,
                    "affected_topics": [tuid],
                    "readiness": prereq_state["readiness"],
                    "hard_blocked": prereq_state["hard_blocked"],
                })
        # latent gaps: topics with low mastery but unlocked
        for r in rows:
            tuid = r["uid"]
            prereq_state = compute_topic_prereq_state(
                topic_uid=tuid,
                prereq_edges=normalize_prereq_edges(r.get("prereqs") or []),
                progress=progress,
                personal_factors=personal_factors,
                readiness_threshold=prereq_threshold,
                hard_threshold=0.5,
            )
            if prereq_state["is_unlocked"] and progress.get(tuid, 0.0) < 0.5:
                latent.append({
                    "topic_uid": tuid,
                    "distance": 1.0 - progress.get(tuid, 0.0),
                    "why": "low_mastery_unlocked",
                    "readiness": prereq_state["readiness"],
                })
    drv.close()
    return {"blocking_gaps": blocking, "latent_gaps": latent}
