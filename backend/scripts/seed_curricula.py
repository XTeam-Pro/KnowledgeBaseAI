#!/usr/bin/env python3
"""
Seed script: создание/обновление curricula и curriculum_nodes в PostgreSQL.

Создаёт три программы:
  RU-OGE-MATH-2026       — ОГЭ Математика, 11 топиков (канонические uid)
  RU-EGE-BASE-MATH-2026  — ЕГЭ Базовый, 8 топиков
  RU-EGE-PROF-MATH-2026  — ЕГЭ Профиль, 15 топиков

Использование (внутри контейнера):
    python /app/scripts/seed_curricula.py [--dry-run]

Скрипт идемпотентен: при повторном запуске обновляет существующие записи,
не дублирует их.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings  # noqa: E402

# ---------------------------------------------------------------------------
# Определения curricula
# ---------------------------------------------------------------------------

CURRICULA = [
    {
        "code": "RU-OGE-MATH-2026",
        "title": "ОГЭ Математика 2026",
        "standard": "ОГЭ",
        "language": "ru",
        "status": "active",
        "nodes": [
            # Порядок соответствует логике изучения (простое → сложное)
            {"order": 1,  "uid": "TOP-MATH-ALGEBRA-TRANSFORMS",    "task": "1"},
            {"order": 2,  "uid": "TOP-MATH-EQUATIONS-SYSTEMS",     "task": "3"},
            {"order": 3,  "uid": "TOP-MATH-INEQUALITIES",          "task": "4"},
            {"order": 4,  "uid": "TOP-MATH-PROGRESSIONS",          "task": "5"},
            {"order": 5,  "uid": "TOP-MATH-PLANE-GEOMETRY",        "task": "6"},
            {"order": 6,  "uid": "TOP-MATH-FUNCTIONS-GRAPHS",      "task": "7-8"},
            {"order": 7,  "uid": "TOP-MATH-PROBABILITY-STATISTICS","task": "10"},
            {"order": 8,  "uid": "TOP-MATH-APPLIED-MATH",          "task": "11"},
            {"order": 9,  "uid": "TOP-MATH-ADVANCED-ALGEBRA",      "task": "12"},
            {"order": 10, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM",   "task": "13"},
            {"order": 11, "uid": "TOP-MATH-ADVANCED-FUNCTIONS",    "task": "14"},
        ],
    },
    {
        "code": "RU-EGE-BASE-MATH-2026",
        "title": "ЕГЭ Базовый Математика 2026",
        "standard": "ЕГЭ Базовый",
        "language": "ru",
        "status": "active",
        "nodes": [
            {"order": 1, "uid": "TOP-MATH-NUMBERS-CALCULATIONS",    "task": "1-3"},
            {"order": 2, "uid": "TOP-MATH-EQUATIONS-SYSTEMS",       "task": "4-5"},
            {"order": 3, "uid": "TOP-MATH-FUNCTIONS-GRAPHS",        "task": "6-8"},
            {"order": 4, "uid": "TOP-MATH-DERIVATIVES",             "task": "9"},
            {"order": 5, "uid": "TOP-MATH-PLANE-GEOMETRY",          "task": "10-12"},
            {"order": 6, "uid": "TOP-MATH-STEREOMETRY",             "task": "13"},
            {"order": 7, "uid": "TOP-MATH-PROBABILITY-STATISTICS",  "task": "14-15"},
            {"order": 8, "uid": "TOP-MATH-APPLIED-MATH",            "task": "16-20"},
        ],
    },
    {
        "code": "RU-EGE-PROF-MATH-2026",
        "title": "ЕГЭ Профиль Математика 2026",
        "standard": "ЕГЭ Профиль",
        "language": "ru",
        "status": "active",
        "nodes": [
            # Часть 1 (задания 1–12)
            {"order": 1,  "uid": "TOP-MATH-EQUATIONS-SYSTEMS",          "task": "1-3"},
            {"order": 2,  "uid": "TOP-MATH-TRIGONOMETRY",               "task": "4-6"},
            {"order": 3,  "uid": "TOP-MATH-EXP-LOG",                    "task": "7-9"},
            {"order": 4,  "uid": "TOP-MATH-CALCULUS",                   "task": "10-11"},
            {"order": 5,  "uid": "TOP-MATH-PLANE-GEOMETRY",             "task": "12"},
            {"order": 6,  "uid": "TOP-MATH-PROBABILITY-STATISTICS",     "task": "1-3"},
            {"order": 7,  "uid": "TOP-MATH-COMBINATORICS",              "task": "1-3"},
            # Часть 2 (задания 13–19)
            {"order": 8,  "uid": "TOP-MATH-ADVANCED-TRIG",              "task": "13"},
            {"order": 9,  "uid": "TOP-MATH-STEREOMETRY-ADVANCED",       "task": "14"},
            {"order": 10, "uid": "TOP-MATH-FINANCIAL-ADVANCED",         "task": "15"},
            {"order": 11, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF",  "task": "16"},
            {"order": 12, "uid": "TOP-MATH-OPTIMIZATION",               "task": "17"},
            {"order": 13, "uid": "TOP-MATH-COMPLEX-INEQUALITIES",       "task": "18"},
            {"order": 14, "uid": "TOP-MATH-NUMBER-THEORY",              "task": "19"},
            {"order": 15, "uid": "TOP-MATH-APPLIED-MATH",               "task": None},
        ],
    },
]


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _get_conn():
    try:
        import psycopg2
        dsn = str(settings.pg_dsn) if settings.pg_dsn else ""
        if not dsn:
            return None
        return psycopg2.connect(dsn)
    except Exception as exc:
        print(f"  [ERROR] Cannot connect to PostgreSQL: {exc}")
        return None


def _upsert_curriculum(cur, code: str, title: str, standard: str,
                       language: str, status: str) -> int:
    """INSERT or UPDATE curriculum; returns curriculum id."""
    cur.execute("SELECT id FROM curricula WHERE code = %s", (code,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE curricula SET title=%s, standard=%s, language=%s, status=%s WHERE code=%s",
            (title, standard, language, status, code),
        )
        return row[0]
    else:
        cur.execute(
            "INSERT INTO curricula(code, title, standard, language, status) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (code, title, standard, language, status),
        )
        return cur.fetchone()[0]


def _upsert_nodes(cur, curriculum_id: int, nodes: list) -> int:
    """Replace all curriculum_nodes for this curriculum."""
    cur.execute("DELETE FROM curriculum_nodes WHERE curriculum_id = %s", (curriculum_id,))
    count = 0
    for n in nodes:
        cur.execute(
            "INSERT INTO curriculum_nodes"
            "(curriculum_id, kind, canonical_uid, order_index, is_required, exam_task_number) "
            "VALUES (%s, 'topic', %s, %s, TRUE, %s)",
            (curriculum_id, n["uid"], n["order"], n.get("task")),
        )
        count += 1
    return count


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

def seed(dry_run: bool = False) -> None:
    conn = _get_conn()
    if conn is None:
        print("PostgreSQL не настроен — пропускаем seeding curriculum.")
        return

    total_curricula = 0
    total_nodes = 0

    try:
        with conn:
            with conn.cursor() as cur:
                for curriculum in CURRICULA:
                    code = curriculum["code"]
                    if dry_run:
                        print(f"  [DRY] curriculum: {code} ({len(curriculum['nodes'])} topics)")
                        for n in curriculum["nodes"]:
                            print(f"        {n['order']:2d}. {n['uid']}  task={n.get('task')}")
                        total_curricula += 1
                        total_nodes += len(curriculum["nodes"])
                        continue

                    cid = _upsert_curriculum(
                        cur,
                        code,
                        curriculum["title"],
                        curriculum["standard"],
                        curriculum["language"],
                        curriculum["status"],
                    )
                    n_nodes = _upsert_nodes(cur, cid, curriculum["nodes"])
                    print(f"  [OK] {code} (id={cid}): {n_nodes} узлов")
                    total_curricula += 1
                    total_nodes += n_nodes
    finally:
        conn.close()

    mode = "(DRY RUN)" if dry_run else "(APPLIED)"
    print()
    print(f"{'=' * 60}")
    print(f"Seed Curricula завершён {mode}")
    print(f"  Curricula : {total_curricula}")
    print(f"  Nodes     : {total_nodes}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed PostgreSQL curriculum records")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    print("Seed Curricula (OGE / EGE-BASE / EGE-PROF)")
    print(f"Режим: {'DRY RUN' if args.dry_run else 'WRITE'}")
    print("=" * 60)
    seed(dry_run=args.dry_run)
