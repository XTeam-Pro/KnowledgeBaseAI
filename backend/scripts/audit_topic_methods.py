#!/usr/bin/env python3
"""
Аудит тем и методов в графе знаний KnowledgeBaseAI.

Проверяет:
  1. Количество методов у каждой темы (цель: >= 3)
  2. Семантическую релевантность методов теме (простая эвристика по ключевым словам)
  3. Темы без навыков (REQUIRES_SKILL)

Использование (внутри контейнера):
    python /app/scripts/audit_topic_methods.py
    python /app/scripts/audit_topic_methods.py --json-out /tmp/audit.json
    python /app/scripts/audit_topic_methods.py --topic TOPIC-MULT-TABLE   # одна тема
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graph.neo4j_repo import Neo4jRepo  # noqa: E402

TENANT_ID = "default"

# ---------------------------------------------------------------------------
# Эвристика: слова из названия темы vs слова из названия метода/навыка.
# Если пересечение пустое — скорее всего нерелевантный метод.
# ---------------------------------------------------------------------------
STOP_WORDS = {
    "и", "в", "на", "с", "по", "для", "из", "к", "от", "а", "но", "или",
    "не", "при", "за", "до", "через", "над", "под", "об", "без", "между",
    "метод", "задача", "алгоритм", "решение", "применение", "анализ",
    "вычисление", "нахождение", "способ", "правило", "формула",
}


def _tokens(text: str) -> set[str]:
    """Минимальная токенизация: нижний регистр, без знаков."""
    import re
    words = re.findall(r"[а-яёa-z]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in STOP_WORDS}


def audit_all_topics(repo: Neo4jRepo, target_uid: str | None = None) -> list[dict]:
    """Возвращает список записей аудита по каждой теме."""

    # 1. Получаем все темы
    where_clause = ""
    params: dict = {"tid": TENANT_ID}
    if target_uid:
        where_clause = "WHERE t.uid = $uid"
        params["uid"] = target_uid

    topics = repo.read(
        f"""
        MATCH (t:Topic {{tenant_id: $tid}})
        {where_clause}
        RETURN t.uid AS uid, t.title AS title, t.description AS description
        ORDER BY t.title
        """,
        params,
    )

    results = []

    for topic in topics:
        uid = topic["uid"]
        title = topic["title"] or ""
        description = topic["description"] or ""

        # 2. Навыки темы
        skills = repo.read(
            """
            MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[:REQUIRES_SKILL]->(sk:Skill)
            RETURN sk.uid AS uid, sk.title AS title
            """,
            {"uid": uid, "tid": TENANT_ID},
        )

        # 3. Методы через навыки
        methods = repo.read(
            """
            MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[:REQUIRES_SKILL]->(sk:Skill)
                  -[:HAS_METHOD]->(m:Method)
            OPTIONAL MATCH (m)-[:HAS_EXAMPLE]->(ex:Example)
            WITH sk, m, count(ex) AS example_count
            RETURN
                sk.uid    AS skill_uid,
                sk.title  AS skill_title,
                m.uid     AS method_uid,
                m.title   AS method_title,
                example_count
            """,
            {"uid": uid, "tid": TENANT_ID},
        )

        # 4. Эвристика релевантности
        topic_tokens = _tokens(title + " " + description)
        irrelevant_methods = []
        for m in methods:
            method_tokens = _tokens(
                (m["method_title"] or "") + " " + (m["skill_title"] or "")
            )
            if topic_tokens and method_tokens and not topic_tokens.intersection(method_tokens):
                irrelevant_methods.append(
                    {
                        "method_uid": m["method_uid"],
                        "method_title": m["method_title"],
                        "skill_uid": m["skill_uid"],
                        "skill_title": m["skill_title"],
                    }
                )

        # 5. Итог по теме
        method_count = len(methods)
        has_enough = method_count >= 3
        has_irrelevant = len(irrelevant_methods) > 0

        status = "OK"
        if not has_enough and has_irrelevant:
            status = "CRITICAL"
        elif not has_enough:
            status = "FEW_METHODS"
        elif has_irrelevant:
            status = "IRRELEVANT_METHODS"

        results.append(
            {
                "uid": uid,
                "title": title,
                "status": status,
                "skill_count": len(skills),
                "method_count": method_count,
                "has_enough_methods": has_enough,
                "irrelevant_method_count": len(irrelevant_methods),
                "skills": [{"uid": s["uid"], "title": s["title"]} for s in skills],
                "methods": [
                    {
                        "skill_uid": m["skill_uid"],
                        "skill_title": m["skill_title"],
                        "method_uid": m["method_uid"],
                        "method_title": m["method_title"],
                        "example_count": m["example_count"],
                    }
                    for m in methods
                ],
                "irrelevant_methods": irrelevant_methods,
            }
        )

    return results


def print_report(results: list[dict]) -> None:
    """Форматированный вывод результатов аудита."""
    total = len(results)
    ok = sum(1 for r in results if r["status"] == "OK")
    few = sum(1 for r in results if r["status"] == "FEW_METHODS")
    irrel = sum(1 for r in results if r["status"] == "IRRELEVANT_METHODS")
    critical = sum(1 for r in results if r["status"] == "CRITICAL")
    no_skills = sum(1 for r in results if r["skill_count"] == 0)

    print("=" * 70)
    print("АУДИТ ТЕМАТИЧЕСКИХ МЕТОДОВ — ГРАФ ЗНАНИЙ")
    print("=" * 70)
    print(f"Всего тем             : {total}")
    print(f"✅  OK (≥ 3 метода)   : {ok}")
    print(f"⚠️  Мало методов (< 3): {few}")
    print(f"🔴 Нерелевантные      : {irrel}")
    print(f"💀 Критично (< 3 + нерел.): {critical}")
    print(f"❌  Без навыков       : {no_skills}")
    print()

    problem_statuses = {"CRITICAL", "FEW_METHODS", "IRRELEVANT_METHODS"}

    for r in results:
        if r["status"] not in problem_statuses:
            continue

        icon = {"CRITICAL": "💀", "FEW_METHODS": "⚠️ ", "IRRELEVANT_METHODS": "🔴"}[r["status"]]
        print(f"{icon} [{r['status']}] {r['uid']}")
        print(f"   Тема     : {r['title']}")
        print(f"   Навыков  : {r['skill_count']} | Методов: {r['method_count']}")

        if r["irrelevant_methods"]:
            print("   🚫 Нерелевантные методы:")
            for m in r["irrelevant_methods"]:
                print(f"      • {m['method_title']} (навык: {m['skill_title']})")

        if r["methods"]:
            print("   📋 Все методы темы:")
            for m in r["methods"]:
                print(f"      → {m['method_title']}")

        print()

    print("=" * 70)
    print("Темы без проблем (OK):")
    for r in results:
        if r["status"] == "OK":
            print(f"  ✅ {r['uid']:40s} | методов: {r['method_count']}")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Аудит тем и методов в Neo4j")
    parser.add_argument(
        "--topic",
        default=None,
        help="uid конкретной темы для аудита (по умолчанию — все темы)",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        metavar="FILE",
        help="Сохранить результат аудита в JSON-файл",
    )
    args = parser.parse_args()

    repo = Neo4jRepo()
    try:
        results = audit_all_topics(repo, target_uid=args.topic)
    finally:
        repo.close()

    print_report(results)

    if args.json_out:
        out = Path(args.json_out)
        out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"\nJSON-отчёт сохранён: {out}")


if __name__ == "__main__":
    main()
