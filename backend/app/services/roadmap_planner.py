from typing import Dict, List, Optional
from app.services.graph import neo4j_repo
from app.services.curriculum.repo import get_graph_view
from app.services.personalization.prereq_weights_repo import get_personal_prereq_weight_factors
from app.services.reasoning.prereq_scoring import (
    compute_topic_prereq_state,
    normalize_prereq_edges,
)

# Hysteresis threshold: only rebuild roadmap if mastery changed by >= 15%
REBUILD_THRESHOLD = 0.15

# In-memory cache for last roadmap per user/subject
_roadmap_cache: Dict[str, Dict] = {}

# Fallback titles for curriculum topic UIDs that may not yet have Topic nodes in Neo4j.
# Used when building stub entries so the roadmap shows human-readable names.
_CURRICULUM_UID_TITLES: Dict[str, str] = {
    # OGE 2026
    "TOP-OGE-PRAKTIKO-ORIENTIROVANNYE-ZADACHI-2026": "Практикоориентированные задачи",
    "TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026": "Анализ таблиц и диаграмм",
    "TOP-OGE-GEOMETRICHESKOE-DOKAZATELSTVO-2026": "Геометрическое доказательство",
    # EGE 2026
    "TOP-EGE-FINANSOVAYA-MATEMATIKA-2026": "Финансовая математика",
    "TOP-EGE-ZADACHI-S-PARAMETROM-2026": "Задачи с параметром",
    "TOP-EGE-TEORIYA-CHISEL-DELIMOST-2026": "Теория чисел. Делимость",
    # Common topic UIDs (in case they're missing from the graph)
    "TOP-MATH-NUMBERS-CALCULATIONS": "Числа и вычисления",
    "TOP-MATH-ALGEBRA-TRANSFORMS": "Алгебраические преобразования",
    "TOP-MATH-EQUATIONS-SYSTEMS": "Уравнения и системы",
    "TOP-MATH-PROBABILITY-STATISTICS": "Вероятность и статистика",
    "TOP-MATH-FUNCTIONS-GRAPHS": "Функции и их графики",
    "TOP-MATH-INEQUALITIES": "Неравенства",
    "TOP-MATH-PROGRESSIONS": "Прогрессии",
    "TOP-MATH-PLANE-GEOMETRY": "Планиметрия",
    "TOP-MATH-ADVANCED-ALGEBRA": "Алгебра: задачи повышенного уровня",
    "TOP-MATH-ADVANCED-FUNCTIONS": "Функции с параметром",
    "TOP-MATH-ADVANCED-PLANE-GEOM": "Планиметрия: задачи повышенного уровня",
    "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF": "Планиметрия с доказательством",
    "TOP-MATH-STEREOMETRY": "Стереометрия",
    "TOP-MATH-STEREOMETRY-ADVANCED": "Стереометрия: повышенный уровень",
    "TOP-MATH-EXP-LOG": "Степени и логарифмы",
    "TOP-MATH-DERIVATIVES": "Производная и интеграл",
    "TOP-MATH-CALCULUS": "Исследование функции",
    "TOP-MATH-APPLIED-MATH": "Математическое моделирование",
    "TOP-MATH-ADVANCED-TRIG": "Тригонометрические уравнения",
    "TOP-MATH-COMPLEX-INEQUALITIES": "Показательные и логарифмические неравенства",
    "TOP-MATH-FINANCIAL-ADVANCED": "Финансово-экономические задачи",
    "TOP-MATH-COMBINATORICS": "Теория вероятностей и комбинаторика",
}

# Student tier configuration: (limit, select_count)
TIER_CONFIG: Dict[str, Dict] = {
    "standard": {"limit": 30, "select": 8},
    "advanced": {"limit": 50, "select": 15},
    "gifted": {"limit": 100, "select": 20},
    "olympiad": {"limit": 100, "select": 20},
}


def should_rebuild_roadmap(
    cache_key: str,
    current_progress: Dict[str, float],
) -> bool:
    """Check if roadmap needs rebuilding based on mastery change threshold."""
    cached = _roadmap_cache.get(cache_key)
    if cached is None:
        return True

    old_progress = cached.get("progress", {})

    # Check if any topic mastery changed by more than threshold
    all_keys = set(old_progress.keys()) | set(current_progress.keys())
    for key in all_keys:
        old_val = float(old_progress.get(key, 0.0))
        new_val = float(current_progress.get(key, 0.0))
        if abs(new_val - old_val) >= REBUILD_THRESHOLD:
            return True

    return False


def _filter_nodes_by_quarter(nodes: List[Dict], quarter: int | None) -> List[Dict]:
    """Keep curriculum nodes up to the given school quarter.

    A node with quarter IS NULL is quarter-agnostic and always kept (e.g. exam
    curricula). When ``quarter`` is None no filtering is applied. Otherwise only
    nodes with ``node.quarter <= quarter`` (or NULL) are returned.
    """
    if quarter is None:
        return list(nodes)
    out: List[Dict] = []
    for n in nodes:
        q = n.get("quarter")
        if q is None or int(q) <= int(quarter):
            out.append(n)
    return out


def plan_route(
    subject_uid: str | None,
    progress: Dict[str, float],
    limit: int = 30,
    penalty_factor: float = 0.15,
    tenant_id: str | None = None,
    curriculum_code: str | None = None,
    force_rebuild: bool = False,
    student_tier: str = "standard",
    user_uid: str | None = None,
    quarter: int | None = None,
) -> List[Dict]:
    # Apply tier-based limit override
    tier_cfg = TIER_CONFIG.get(student_tier, TIER_CONFIG["standard"])
    effective_limit = max(limit, tier_cfg["limit"])
    select_count = tier_cfg["select"]

    # Hysteresis check
    cache_key = f"{tenant_id or ''}:{subject_uid or ''}:{curriculum_code or ''}:{student_tier}:{user_uid or ''}:q{quarter or ''}"
    if not force_rebuild and not should_rebuild_roadmap(cache_key, progress):
        cached = _roadmap_cache.get(cache_key, {})
        if cached.get("items"):
            return cached["items"]
    drv = neo4j_repo.get_driver()
    items: List[Dict] = []
    s = drv.session()

    # Curriculum filter set
    allowed_topics = set()
    root_nodes: List[str] = []
    if curriculum_code:
        cv = get_graph_view(curriculum_code)
        if cv.get("ok") and cv.get("nodes"):
            # Use only the explicitly seeded curriculum nodes — no PREREQ expansion.
            # Prerequisites are used for ordering/priority scoring only (lines below),
            # not as additional roadmap nodes.
            cv_nodes = _filter_nodes_by_quarter(cv["nodes"], quarter)
            root_nodes = [n["canonical_uid"] for n in cv_nodes if n.get("canonical_uid")]
            allowed_topics = set(root_nodes)

    # Define query filter
    tid_filter_sub = "WHERE sub.tenant_id = $tid" if tenant_id else ""
    tid_filter_node = "WHERE ($tid IS NULL OR t.tenant_id = $tid)"

    # Include difficulty_level in query for advanced tier priority bonus
    # When curriculum is set and we have allowed_topics, query those directly
    # (curriculum topics may not be connected via CONTAINS to the Subject)
    if curriculum_code and allowed_topics:
        rows = s.run(
            "UNWIND $uids AS uid MATCH (t:Topic {uid: uid}) "
            "WHERE ($tid IS NULL OR t.tenant_id = $tid) "
            "OPTIONAL MATCH (t)-[pr:PREREQ]->(pre:Topic) "
            "RETURN t.uid AS uid, t.title AS title, collect(DISTINCT {uid: pre.uid, weight: coalesce(pr.weight, 0.5), is_hard: coalesce(pr.is_hard, false)}) AS prereqs, "
            "coalesce(t.difficulty_level, 5) AS difficulty_level",
            {"uids": list(allowed_topics), "tid": tenant_id}
        ).data()
    elif subject_uid:
        # Graph traversal: Subject → Section → Topic OR Subject → Section → Subsection → Topic
        query = (
            "MATCH (sub:Subject {uid:$su})-[:CONTAINS*2..3]->(t:Topic) "
            "WHERE ($tid IS NULL OR sub.tenant_id = $tid) "
            "AND ($tid IS NULL OR t.tenant_id = $tid) "
            "OPTIONAL MATCH (t)-[pr:PREREQ]->(pre:Topic) "
            "RETURN DISTINCT t.uid AS uid, t.title AS title, collect(DISTINCT {uid: pre.uid, weight: coalesce(pr.weight, 0.5), is_hard: coalesce(pr.is_hard, false)}) AS prereqs, "
            "coalesce(t.difficulty_level, 5) AS difficulty_level"
        )
        rows = s.run(query, {"su": subject_uid, "tid": tenant_id}).data()
    else:
        rows = s.run(
            "MATCH (t:Topic) WHERE ($tid IS NULL OR t.tenant_id = $tid) "
            "OPTIONAL MATCH (t)-[pr:PREREQ]->(pre:Topic) "
            "RETURN t.uid AS uid, t.title AS title, collect(DISTINCT {uid: pre.uid, weight: coalesce(pr.weight, 0.5), is_hard: coalesce(pr.is_hard, false)}) AS prereqs, "
            "coalesce(t.difficulty_level, 5) AS difficulty_level",
            {"tid": tenant_id}
        ).data()

    is_advanced = student_tier in ("gifted", "olympiad")
    personal_factors = get_personal_prereq_weight_factors(
        user_uid=user_uid,
        topic_uids=[r.get("uid") for r in rows if r.get("uid")],
        tenant_id=tenant_id,
    )

    for r in rows:
        tuid = r["uid"]

        # PRISM FILTER
        if curriculum_code and tuid not in allowed_topics:
            continue

        mastered = float(progress.get(tuid, 0.0) or 0.0)
        prereq_edges = normalize_prereq_edges(r.get("prereqs") or [])
        prereq_state = compute_topic_prereq_state(
            topic_uid=tuid,
            prereq_edges=prereq_edges,
            progress=progress,
            personal_factors=personal_factors,
            readiness_threshold=0.3,
            hard_threshold=0.5,
        )
        missing = len(prereq_state["blocking_prereqs"]) + len(prereq_state["soft_missing_prereqs"])
        difficulty = float(r.get("difficulty_level", 5))
        priority = max(0.0, (1.0 - mastered) + penalty_factor * prereq_state["soft_gap"])
        if prereq_state["hard_blocked"]:
            priority += penalty_factor
        # Difficulty bonus for gifted/olympiad: prefer harder topics
        if is_advanced:
            priority += 0.1 * (difficulty / 10.0)
        items.append(
            {
                "uid": tuid,
                "title": r["title"],
                "mastered": mastered,
                "missing_prereqs": missing,
                "priority": priority,
                "difficulty_level": difficulty,
                "readiness": prereq_state["readiness"],
                "is_hard_blocked": prereq_state["hard_blocked"],
            }
        )
    try:
        s.close()
    except Exception:
        pass
    drv.close()
    items.sort(key=lambda x: x["priority"], reverse=True)

    # When curriculum is set, return ALL curriculum topics.
    # Add stubs for curriculum root nodes not found in Neo4j so the full
    # curriculum always appears on the roadmap regardless of graph completeness.
    if curriculum_code:
        found_uids = {it["uid"] for it in items}
        seen_stubs: set = set()
        for uid in root_nodes:
            if uid and uid not in found_uids and uid not in seen_stubs:
                seen_stubs.add(uid)
                mastered = float(progress.get(uid, 0.0) or 0.0)
                items.append({
                    "uid": uid,
                    "title": _CURRICULUM_UID_TITLES.get(uid, uid),
                    "mastered": mastered,
                    "missing_prereqs": 0,
                    "priority": max(0.0, 1.0 - mastered),
                    "difficulty_level": 5,
                })
        items.sort(key=lambda x: x["priority"], reverse=True)
        # Return ALL curriculum topics — no tier-based cap for exam curricula
        _roadmap_cache[cache_key] = {"items": items, "progress": dict(progress)}
        return items

    if len(items) >= effective_limit:
        result = items[:effective_limit]
        # Apply branch grouping for gifted/olympiad tiers
        if student_tier in ("gifted", "olympiad"):
            result = _group_by_branch(result, select_count, progress)
        else:
            result = result[:select_count]
        _roadmap_cache[cache_key] = {"items": result, "progress": dict(progress)}
        return result

    # Fallback search if not enough items
    if subject_uid:
        s2 = neo4j_repo.get_driver().session()
        try:
            more = s2.run(
                "MATCH (t:Topic) WHERE ($tid IS NULL OR t.tenant_id = $tid) "
                "AND (t)<-[:CONTAINS]-() "
                "OPTIONAL MATCH (t)-[pr:PREREQ]->(pre:Topic) "
                "RETURN DISTINCT t.uid AS uid, t.title AS title, collect(DISTINCT {uid: pre.uid, weight: coalesce(pr.weight, 0.5), is_hard: coalesce(pr.is_hard, false)}) AS prereqs, "
                "coalesce(t.difficulty_level, 5) AS difficulty_level",
                {"tid": tenant_id}
            ).data()
        finally:
            try:
                s2.close()
            except Exception:
                ...
        for r in more:
            tuid = r["uid"]
            if curriculum_code and allowed_topics and tuid not in allowed_topics:
                continue
            if any(it["uid"] == tuid for it in items):
                continue
            mastered = float(progress.get(tuid, 0.0) or 0.0)
            prereq_edges = normalize_prereq_edges(r.get("prereqs") or [])
            prereq_state = compute_topic_prereq_state(
                topic_uid=tuid,
                prereq_edges=prereq_edges,
                progress=progress,
                personal_factors=personal_factors,
                readiness_threshold=0.3,
                hard_threshold=0.5,
            )
            missing = len(prereq_state["blocking_prereqs"]) + len(prereq_state["soft_missing_prereqs"])
            difficulty = float(r.get("difficulty_level", 5))
            priority = max(0.0, (1.0 - mastered) + penalty_factor * prereq_state["soft_gap"])
            if prereq_state["hard_blocked"]:
                priority += penalty_factor
            if is_advanced:
                priority += 0.1 * (difficulty / 10.0)
            items.append(
                {
                    "uid": tuid,
                    "title": r["title"],
                    "mastered": mastered,
                    "missing_prereqs": missing,
                    "priority": priority,
                    "difficulty_level": difficulty,
                    "readiness": prereq_state["readiness"],
                    "is_hard_blocked": prereq_state["hard_blocked"],
                }
            )
        items.sort(key=lambda x: x["priority"], reverse=True)
        if items and len(items) >= effective_limit:
            return items[:select_count]

        if items and len(items) < effective_limit and progress:
            present = {it["uid"] for it in items}
            for tuid, mastered in progress.items():
                if tuid in present:
                    continue
                try:
                    mastered_f = float(mastered or 0.0)
                except Exception:
                    mastered_f = 0.0
                items.append({"uid": tuid, "title": tuid, "mastered": mastered_f, "missing_prereqs": 0, "priority": max(0.0, 1.0 - mastered_f), "difficulty_level": 5})
                if len(items) >= effective_limit:
                    break
            items.sort(key=lambda x: x["priority"], reverse=True)
            if items:
                return items[:select_count]
    # Fallback 1: use progress keys as topics (prefer known user context)
    fallback: List[Dict] = []
    if progress:
        for tuid, mastered in progress.items():
            try:
                mastered_f = float(mastered or 0.0)
            except Exception:
                mastered_f = 0.0
            priority = max(0.0, (1.0 - mastered_f))
            fallback.append({"uid": tuid, "title": tuid, "mastered": mastered_f, "missing_prereqs": 0, "priority": priority, "difficulty_level": 5})
            if len(fallback) >= effective_limit:
                break
        fallback.sort(key=lambda x: x["priority"], reverse=True)
        return fallback[:select_count]
    # Fallback 2: synthesize starter topics
    for i in range(select_count):
        tuid = f"TOP-STUB-{i+1}"
        fallback.append({"uid": tuid, "title": f"Стартовая тема {i+1}", "mastered": 0.0, "missing_prereqs": 0, "priority": 1.0, "difficulty_level": 5})
    result = fallback[:select_count]
    _roadmap_cache[cache_key] = {"items": result, "progress": dict(progress)}
    return result


def _group_by_branch(items: List[Dict], total_select: int, progress: Dict[str, float]) -> List[Dict]:
    """Group items into multi-branch structure for gifted/olympiad students.

    Branches:
    - fast_track: required high-priority unmastered topics (5-8)
    - deep_dive: advanced depth on partially mastered areas (3-5)
    - breadth: cross-topic connections, lower priority (3-5)
    """
    fast_track: List[Dict] = []
    deep_dive: List[Dict] = []
    breadth: List[Dict] = []

    for item in items:
        mastered = item.get("mastered", 0.0)
        difficulty = item.get("difficulty_level", 5)

        if mastered < 0.3 and item.get("priority", 0) > 0.5:
            item["branch_type"] = "fast_track"
            fast_track.append(item)
        elif 0.3 <= mastered < 0.85 and difficulty >= 5:
            item["branch_type"] = "deep_dive"
            deep_dive.append(item)
        else:
            item["branch_type"] = "breadth"
            breadth.append(item)

    # Select within limits: fast_track 5-8, deep_dive 3-5, breadth 3-5
    selected = fast_track[:8] + deep_dive[:5] + breadth[:5]
    # Trim to total_select
    return selected[:total_select]
