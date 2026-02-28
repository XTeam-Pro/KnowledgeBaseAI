#!/usr/bin/env python3
"""
Seed script: создание/обновление curricula и curriculum_nodes в PostgreSQL.

Создаёт три программы по структуре ФИПИ КИМ 2026:
  RU-OGE-MATH-2026       — ОГЭ Математика, 25 заданий
  RU-EGE-BASE-MATH-2026  — ЕГЭ Базовый, 21 задание
  RU-EGE-PROF-MATH-2026  — ЕГЭ Профиль, 19 заданий

Маппинг задание → Topic UID соответствует спецификации и
кодификатору ФИПИ 2026.

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
# Определения curricula — ФИПИ КИМ 2026
# ---------------------------------------------------------------------------

CURRICULA = [
    # ==================================================================
    # ОГЭ Математика 2026 — 25 заданий (Ч1: 1-19 краткий, Ч2: 20-25 развёрнутый)
    # Спецификация: https://fipi.ru/oge/demoversii-specifikacii-kodifikatory
    # ==================================================================
    {
        "code": "RU-OGE-MATH-2026",
        "title": "ОГЭ Математика 2026",
        "standard": "ОГЭ",
        "language": "ru",
        "status": "active",
        "nodes": [
            # --- Практико-ориентированный блок (задания 1-5) ---
            {"order": 1,  "uid": "TOP-OGE-PRAKTIKO-ORIENTIROVANNYE-ZADACHI-2026", "task": "1"},
            {"order": 2,  "uid": "TOP-MATH-NUMBERS-CALCULATIONS",                "task": "2,6"},
            {"order": 3,  "uid": "TOP-EDINITSY-IZMERENIYA-002",                   "task": "3"},
            {"order": 4,  "uid": "TOP-MATH-APPLIED-MATH",                         "task": "4"},
            {"order": 5,  "uid": "TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026",       "task": "5"},
            # --- Алгебра (задания 6-14) ---
            {"order": 6,  "uid": "TOP-MATH-ALGEBRA-TRANSFORMS",                  "task": "7,8,12"},
            {"order": 7,  "uid": "TOP-MATH-EQUATIONS-SYSTEMS",                   "task": "9"},
            {"order": 8,  "uid": "TOP-MATH-PROBABILITY-STATISTICS",              "task": "10,19"},
            {"order": 9,  "uid": "TOP-MATH-FUNCTIONS-GRAPHS",                    "task": "11"},
            {"order": 10, "uid": "TOP-MATH-INEQUALITIES",                        "task": "13"},
            {"order": 11, "uid": "TOP-MATH-PROGRESSIONS",                        "task": "14"},
            # --- Геометрия (задания 15-19) ---
            {"order": 12, "uid": "TOP-UGLY-9cbfc3",                              "task": "15"},
            {"order": 13, "uid": "TOP-PERIMETR-I-PLOSHCHAD-003",                 "task": "16"},
            {"order": 14, "uid": "TOP-MATH-PLANE-GEOMETRY",                      "task": "17,18"},
            # --- Часть 2: развёрнутый ответ (задания 20-25) ---
            {"order": 15, "uid": "TOP-MATH-ADVANCED-ALGEBRA",                    "task": "20"},
            {"order": 16, "uid": "TOP-TEKSTOVYE-ZADACHI-004",                    "task": "21"},
            {"order": 17, "uid": "TOP-MATH-ADVANCED-FUNCTIONS",                  "task": "22"},
            {"order": 18, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM",                 "task": "23,25"},
            {"order": 19, "uid": "TOP-OGE-GEOMETRICHESKOE-DOKAZATELSTVO-2026",   "task": "24"},
        ],
    },
    # ==================================================================
    # ЕГЭ Базовый Математика 2026 — 21 задание (все — краткий ответ)
    # Спецификация: https://fipi.ru/ege/demoversii-specifikacii-kodifikatory
    # ==================================================================
    {
        "code": "RU-EGE-BASE-MATH-2026",
        "title": "ЕГЭ Базовый Математика 2026",
        "standard": "ЕГЭ Базовый",
        "language": "ru",
        "status": "active",
        "nodes": [
            # Вычисления и преобразования
            {"order": 1,  "uid": "TOP-MATH-NUMBERS-CALCULATIONS",    "task": "1,15,19"},
            {"order": 2,  "uid": "TOP-TEKSTOVYE-ZADACHI-004",        "task": "2,20"},
            {"order": 3,  "uid": "TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026", "task": "3"},
            {"order": 4,  "uid": "TOP-EDINITSY-IZMERENIYA-002",      "task": "4"},
            {"order": 5,  "uid": "TOP-MATH-PROBABILITY-STATISTICS",  "task": "5,8"},
            # Графики и функции
            {"order": 6,  "uid": "TOP-MATH-APPLIED-MATH",            "task": "6"},
            {"order": 7,  "uid": "TOP-MATH-FUNCTIONS-GRAPHS",        "task": "7"},
            # Планиметрия и стереометрия
            {"order": 8,  "uid": "TOP-PERIMETR-I-PLOSHCHAD-003",     "task": "9"},
            {"order": 9,  "uid": "TOP-MATH-PLANE-GEOMETRY",          "task": "10,12"},
            {"order": 10, "uid": "TOP-MATH-STEREOMETRY",             "task": "11,13"},
            # Преобразования и уравнения
            {"order": 11, "uid": "TOP-MATH-ALGEBRA-TRANSFORMS",      "task": "14,16"},
            {"order": 12, "uid": "TOP-MATH-EQUATIONS-SYSTEMS",       "task": "17"},
            {"order": 13, "uid": "TOP-MATH-INEQUALITIES",            "task": "18"},
            # Комплексные задачи
            {"order": 14, "uid": "TOP-MATH-ADVANCED-ALGEBRA",        "task": "21"},
        ],
    },
    # ==================================================================
    # ЕГЭ Профиль Математика 2026 — 19 заданий
    # Часть 1 (1-12): краткий ответ; Часть 2 (13-19): развёрнутый ответ
    # Спецификация: https://fipi.ru/ege/demoversii-specifikacii-kodifikatory
    # ==================================================================
    {
        "code": "RU-EGE-PROF-MATH-2026",
        "title": "ЕГЭ Профиль Математика 2026",
        "standard": "ЕГЭ Профиль",
        "language": "ru",
        "status": "active",
        "nodes": [
            # --- Часть 1 (задания 1–12, краткий ответ) ---
            {"order": 1,  "uid": "TOP-MATH-PLANE-GEOMETRY",              "task": "1"},
            {"order": 2,  "uid": "TOP-VEKTORY-78d40c",                   "task": "2"},
            {"order": 3,  "uid": "TOP-MATH-STEREOMETRY",                 "task": "3"},
            {"order": 4,  "uid": "TOP-MATH-PROBABILITY-STATISTICS",      "task": "4"},
            {"order": 5,  "uid": "TOP-MATH-COMBINATORICS",               "task": "5"},
            {"order": 6,  "uid": "TOP-MATH-EQUATIONS-SYSTEMS",           "task": "6"},
            {"order": 7,  "uid": "TOP-MATH-EXP-LOG",                     "task": "7"},
            {"order": 8,  "uid": "TOP-MATH-DERIVATIVES",                 "task": "8"},
            {"order": 9,  "uid": "TOP-MATH-APPLIED-MATH",                "task": "9"},
            {"order": 10, "uid": "TOP-TEKSTOVYE-ZADACHI-004",            "task": "10"},
            {"order": 11, "uid": "TOP-MATH-FUNCTIONS-GRAPHS",            "task": "11,12"},
            # --- Часть 2 (задания 13–19, развёрнутый ответ) ---
            {"order": 13, "uid": "TOP-MATH-ADVANCED-TRIG",               "task": "13"},
            {"order": 14, "uid": "TOP-MATH-STEREOMETRY-ADVANCED",        "task": "14"},
            {"order": 15, "uid": "TOP-MATH-COMPLEX-INEQUALITIES",        "task": "15"},
            {"order": 16, "uid": "TOP-MATH-FINANCIAL-ADVANCED",          "task": "16"},
            {"order": 17, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF",   "task": "17"},
            {"order": 18, "uid": "TOP-EGE-ZADACHI-S-PARAMETROM-2026",    "task": "18"},
            {"order": 19, "uid": "TOP-EGE-TEORIYA-CHISEL-DELIMOST-2026", "task": "19"},
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
