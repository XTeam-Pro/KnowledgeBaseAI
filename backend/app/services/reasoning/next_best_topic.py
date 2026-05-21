from typing import Dict, List
from app.services.graph.neo4j_repo import get_driver
from app.services.personalization.prereq_weights_repo import get_personal_prereq_weight_factors
from app.services.reasoning.prereq_scoring import (
    compute_topic_prereq_state,
    normalize_prereq_edges,
)


def next_best_topics(
    subject_uid: str,
    progress: Dict[str, float],
    prereq_threshold: float = 0.7,
    top_k: int = 5,
    alpha: float = 0.5,
    beta: float = 0.3,
    user_uid: str | None = None,
    tenant_id: str | None = None,
) -> Dict[str, List[Dict]]:
    drv = get_driver()
    items: List[Dict] = []
    with drv.session() as s:
        rows = s.run(
            "MATCH (sub:Subject {uid:$su})-[:CONTAINS]->(:Section)-[:CONTAINS]->(t:Topic) "
            "WHERE ($tid IS NULL OR sub.tenant_id = $tid) "
            "AND ($tid IS NULL OR t.tenant_id = $tid) "
            "OPTIONAL MATCH (t)-[pr:PREREQ]->(pre:Topic) "
            "WITH t, collect({uid: pre.uid, weight: coalesce(pr.weight, 0.5), is_hard: coalesce(pr.is_hard, false)}) AS prereqs "
            "OPTIONAL MATCH (x:Topic)-[:PREREQ]->(t) WITH t, prereqs, COUNT(x) AS in_deg "
            "OPTIONAL MATCH path=(t)-[:PREREQ*1..10]->(d:Topic) WITH t, prereqs, in_deg, COUNT(DISTINCT d) AS descendants "
            "RETURN t.uid AS uid, t.title AS title, prereqs, in_deg, descendants",
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
            if not prereq_state["is_unlocked"]:
                continue
            mastery = float(progress.get(tuid, 0.0))
            need = 1.0 - mastery
            importance = float(r["in_deg"] or 0.0)
            unlock_impact = float(r["descendants"] or 0.0)
            score = need * (1.0 + alpha * importance + beta * unlock_impact)
            items.append({
                "topic_uid": tuid,
                "title": r["title"],
                "mastery": mastery,
                "score": score,
                "reasoning": {
                    "need": need,
                    "importance": importance,
                    "unlock_impact": unlock_impact,
                    "prereqs": [p["uid"] for p in normalize_prereq_edges(r.get("prereqs") or [])],
                    "readiness": prereq_state["readiness"],
                }
            })
    drv.close()
    items.sort(key=lambda x: x["score"], reverse=True)
    return {"items": items[:top_k]}
