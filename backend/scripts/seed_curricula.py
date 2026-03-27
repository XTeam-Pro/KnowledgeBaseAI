#!/usr/bin/env python3
"""
Seed script: создание/обновление curricula и curriculum_nodes в PostgreSQL.

Создаёт три программы по структуре ФИПИ КИМ 2026:
  RU-OGE-MATH-2026       — ОГЭ Математика, 25 заданий
  RU-EGE-BASE-MATH-2026  — ЕГЭ Базовый, 21 задание
  RU-EGE-PROF-MATH-2026  — ЕГЭ Профиль, 19 заданий

Темы соответствуют финальному состоянию графа БЗ (59 обработанных топиков).
Сгенерировано по: docs/graph_update.md (2026-03-26).

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
# Источник тем: docs/graph_update.md, критерий: learning_order_status=processed
# ---------------------------------------------------------------------------

CURRICULA = [
    # ==================================================================
    # ОГЭ Математика 2026 — 25 заданий
    # Ч1 (1–19): краткий ответ, 1 балл; Ч2 (20–25): развёрнутый, до 2 баллов
    # Источник: КИМ ФИПИ 2026, спецификация МА-9 ОГЭ 2026_СПЕЦ
    #
    # Топики: все темы из БЗ с class_range начинающимся ≤ 9.
    # Геометрические задания (15-18, 23-25) ещё не в БЗ → оставлены
    # как заглушки до появления в графе.
    # ==================================================================
    {
        "code": "RU-OGE-MATH-2026",
        "title": "ОГЭ Математика 2026",
        "standard": "ОГЭ",
        "language": "ru",
        "status": "active",
        "nodes": [
            # --- Числа и вычисления (задания 6–7) ---
            {"order": 1,  "uid": "TOP-5-VYRAZHENIYA-I-URAVNENIYA",                         "task": "6,7"},
            {"order": 2,  "uid": "TOP-6-POLOZHITELNYE-I-OTRITSATELNYE-CHISLA",             "task": "6"},
            {"order": 3,  "uid": "TOP-6-DEJSTVIYA-SO-SMESHANNYMI-CHISLAMI",                "task": "6"},
            {"order": 4,  "uid": "TOP-7-RATSIONALNYE-CHISLA",                              "task": "6,7"},
            {"order": 5,  "uid": "TOP-8-STANDARTNYJ-VID-CHISLA",                           "task": "6"},
            {"order": 6,  "uid": "TOP-DEJSTVITELNYE-CHISLA-b50b77",                        "task": "6"},
            # --- Алгебраические выражения (задания 8, 12) ---
            {"order": 7,  "uid": "TOP-7-STEPEN-S-NATURALNYM-POKAZATELEM",                  "task": "8"},
            {"order": 8,  "uid": "TOP-7-RATSIONALNYE-VYRAZHENIYA",                         "task": "8,12"},
            {"order": 9,  "uid": "TOP-7-FAKTORIZACIYA-MNOGOCHLENOV",                       "task": "8"},
            {"order": 10, "uid": "TOP-8-KVADRATNYJ-TREHCHLEN",                             "task": "8,12"},
            {"order": 11, "uid": "TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM",                 "task": "12"},
            {"order": 12, "uid": "TOP-KORNEVYE-FUNKTSII-2a9a47",                           "task": "12"},
            # --- Уравнения и системы (задание 9, 20) ---
            {"order": 13, "uid": "TOP-LINEJNYE-URAVNENIYA-94fc09",                         "task": "9"},
            {"order": 14, "uid": "TOP-7-LINEJNYE-URAVNENIYA-S-DVUMYA-PEREMENNYMI",         "task": "9"},
            {"order": 15, "uid": "TOP-7-SISTEMY-LINEJNYH-URAVNENIJ",                       "task": "9"},
            {"order": 16, "uid": "TOP-KVADRATNYE-URAVNENIYA-0fdb01",                       "task": "9,20"},
            {"order": 17, "uid": "TOP-8-SISTEMY-LINEJNYH-URAVNENIJ-S-DVUMYA-PEREMENNYMI-20260322", "task": "9,20"},
            # --- Вероятность и комбинаторика (задание 10) ---
            {"order": 18, "uid": "TOP-VEROYATNOST-d3cd07",                                 "task": "10"},
            {"order": 19, "uid": "TOP-9-ELEMENTY-KOMBINATORIKI",                           "task": "10"},
            # --- Функции и графики (задания 11, 22) ---
            {"order": 20, "uid": "TOP-7-FUNKCII-I-GRAFIKI",                                "task": "11"},
            {"order": 21, "uid": "TOP-8-FUNKCIYA-I-EE-SVOYSTVA",                           "task": "11"},
            {"order": 22, "uid": "TOP-8-SVOYSTVA-NEKOTORYH-VIDOV-FUNKCIJ",                 "task": "11"},
            {"order": 23, "uid": "TOP-9-FUNKCII-I-IX-SVOYSTVA",                            "task": "11,22"},
            {"order": 24, "uid": "TOP-9-KVADRATICHNAYA-FUNKCIYA-I-GRAFIK",                 "task": "11,22"},
            {"order": 25, "uid": "TOP-STEPENNAYA-FUNKCIYA-9-10",                           "task": "11"},
            {"order": 26, "uid": "TOP-OBRATNAYA-FUNKCIYA-9-10",                            "task": "11"},
            # --- Неравенства (задание 13) ---
            {"order": 27, "uid": "TOP-LINEJNYE-NERAVENSTVA-f61cf0",                        "task": "13"},
            {"order": 28, "uid": "TOP-KVADRATNYE-NERAVENSTVA-f1ebc9",                      "task": "13"},
            {"order": 29, "uid": "TOP-9-NERAVENSTVA-I-SISTEMY-S-DVUMYA-PEREMENNYMI-20260322", "task": "13"},
            # --- Прогрессии (задание 14) ---
            {"order": 30, "uid": "TOP-9-AP",                                               "task": "14"},
            {"order": 31, "uid": "TOP-9-ARIFMETICHESKAYA-PROGRESSIYA",                     "task": "14"},
            {"order": 32, "uid": "TOP-9-GP",                                               "task": "14"},
            # --- Геометрия (задания 15–18, 23–25) — заглушки до появления в БЗ ---
            {"order": 33, "uid": "TOP-6-SIMMETRIYA-I-KRUG",                                "task": "16"},
            {"order": 34, "uid": "TOP-PERIMETR-I-PLOSHCHAD-003",                           "task": "15,23"},
            {"order": 35, "uid": "TOP-OKRUZHNOST-926fe8",                                  "task": "16"},
            {"order": 36, "uid": "TOP-MATH-PLANE-GEOMETRY",                                "task": "17,18,23"},
            {"order": 37, "uid": "TOP-OGE-GEOMETRICHESKOE-DOKAZATELSTVO-2026",             "task": "24"},
            {"order": 38, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM",                           "task": "25"},
            # --- Математические рассуждения и индукция (задание 19, 20) ---
            {"order": 39, "uid": "TOP-9-MATEMATICHESKAYA-INDUKCIYA",                       "task": "20"},
            # --- Вероятность расширенная (смежна с задания 10) ---
            {"order": 40, "uid": "TOP-OSNOVY-TEORII-VEROYATNOS-c8e176",                    "task": "10"},
            # --- Текстовые задачи (задание 21) ---
            {"order": 41, "uid": "TOP-TEKSTOVYE-ZADACHI-004",                              "task": "21"},
        ],
    },
    # ==================================================================
    # ЕГЭ Базовый Математика 2026 — 21 задание (все краткий ответ, базовый уровень)
    # Максимум 21 балл, время 3 часа
    # Источник: КИМ ФИПИ 2026, спецификация МА-11 ЕГЭ 2026 СПЕЦ_базовый
    #
    # Топики: все темы ОГЭ + базовые темы 10–11 класса.
    # ==================================================================
    {
        "code": "RU-EGE-BASE-MATH-2026",
        "title": "ЕГЭ Базовый Математика 2026",
        "standard": "ЕГЭ Базовый",
        "language": "ru",
        "status": "active",
        # Принцип: только темы, прямо тестируемые в ЕГЭ Базовый.
        # Темы 5–7 класса (числа, дроби, натуральные степени) — пресреквизиты;
        # roadmap planner раскрывает их через PREREQ-цепочку автоматически.
        "nodes": [
            # --- Задания 1, 15: числа, степени, корни — вычисления ---
            {"order": 1,  "uid": "TOP-7-RATSIONALNYE-CHISLA",                              "task": "1,15"},
            {"order": 2,  "uid": "TOP-8-STANDARTNYJ-VID-CHISLA",                           "task": "1"},
            {"order": 3,  "uid": "TOP-DEJSTVITELNYE-CHISLA-b50b77",                        "task": "1,15"},
            # --- Задания 4, 14, 16: алгебраические преобразования ---
            {"order": 4,  "uid": "TOP-7-RATSIONALNYE-VYRAZHENIYA",                         "task": "4,14"},
            {"order": 5,  "uid": "TOP-8-KVADRATNYJ-TREHCHLEN",                             "task": "4,14"},
            {"order": 6,  "uid": "TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM",                 "task": "14"},
            {"order": 7,  "uid": "TOP-KORNEVYE-FUNKTSII-2a9a47",                           "task": "14,16"},
            {"order": 8,  "uid": "TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea",                   "task": "16,17"},
            # --- Задание 17: уравнения (рациональные, квадратные, показательные) ---
            {"order": 9,  "uid": "TOP-KVADRATNYE-URAVNENIYA-0fdb01",                       "task": "17"},
            {"order": 10, "uid": "TOP-7-SISTEMY-LINEJNYH-URAVNENIJ",                       "task": "17"},
            {"order": 11, "uid": "TOP-10-POKAZATELNYE-URAVNENIYA",                         "task": "17"},
            # --- Задание 18: неравенства ---
            {"order": 12, "uid": "TOP-LINEJNYE-NERAVENSTVA-f61cf0",                        "task": "18"},
            {"order": 13, "uid": "TOP-KVADRATNYE-NERAVENSTVA-f1ebc9",                      "task": "18"},
            {"order": 14, "uid": "TOP-10-POKAZATELNYE-NERAVENSTVA",                        "task": "18"},
            {"order": 15, "uid": "TOP-LOGARIFMICHESKIE-NERAVENSTVA",                       "task": "18"},
            # --- Задание 5: вероятность ---
            {"order": 16, "uid": "TOP-VEROYATNOST-d3cd07",                                 "task": "5"},
            {"order": 17, "uid": "TOP-OSNOVY-TEORII-VEROYATNOS-c8e176",                    "task": "5"},
            # --- Задания 3, 6: статистика, таблицы, диаграммы ---
            {"order": 18, "uid": "TOP-11-STATISTIKA-I-ANALIZ-DANNYH",                      "task": "3,6"},
            # --- Задание 7: функции — описание поведения, производная ---
            {"order": 19, "uid": "TOP-9-FUNKCII-I-IX-SVOYSTVA",                            "task": "7"},
            {"order": 20, "uid": "TOP-9-KVADRATICHNAYA-FUNKCIYA-I-GRAFIK",                 "task": "7"},
            {"order": 21, "uid": "TOP-STEPENNAYA-FUNKCIYA-9-10",                           "task": "7"},
            {"order": 22, "uid": "TOP-OBRATNAYA-FUNKCIYA-9-10",                            "task": "7"},
            {"order": 23, "uid": "TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f",                       "task": "7,21"},
            {"order": 24, "uid": "TOP-PRAVILA-DIFFERENTSIROVANIYA-3bd912",                 "task": "7"},
            {"order": 25, "uid": "TOP-PROIZVODNAYA-cfd26d",                                "task": "7"},
            {"order": 26, "uid": "TOP-11-GEOMETRICHESKIJ-SMYSL-PROIZVODNOJ",               "task": "7"},
            # --- Задание 20: текстовые задачи с прогрессиями ---
            {"order": 27, "uid": "TOP-9-AP",                                               "task": "20"},
            {"order": 28, "uid": "TOP-9-ARIFMETICHESKAYA-PROGRESSIYA",                     "task": "20"},
            {"order": 29, "uid": "TOP-9-GP",                                               "task": "20"},
            # --- Задания 9,10,12: планиметрия — заглушки до появления в БЗ ---
            {"order": 30, "uid": "TOP-MATH-PLANE-GEOMETRY",                                "task": "9,10,12"},
            # --- Задания 11,13: стереометрия — заглушка ---
            {"order": 31, "uid": "TOP-MATH-STEREOMETRY",                                   "task": "11,13"},
            # --- Задания 2, 20: текстовые задачи ---
            {"order": 32, "uid": "TOP-TEKSTOVYE-ZADACHI-004",                              "task": "2,20"},
            # --- Задание 19: финансовая математика ---
            {"order": 33, "uid": "TOP-EGE-FINANSOVAYA-MATEMATIKA-2026",                    "task": "19"},
        ],
    },
    # ==================================================================
    # ЕГЭ Профиль Математика 2026 — 19 заданий
    # Ч1 (1–12): краткий ответ; Ч2 (13–19): развёрнутый ответ
    # Источник: КИМ ФИПИ 2026, спецификация МА-11 ЕГЭ 2026 СПЕЦ_профильный
    #
    # Принцип: только темы, ПРЯМО тестируемые в заданиях ЕГЭ Профиль
    # (9–11 класс). Темы 5–8 класса — пресреквизиты; roadmap planner
    # раскрывает их автоматически через PREREQ-цепочку в Neo4j.
    # ==================================================================
    {
        "code": "RU-EGE-PROF-MATH-2026",
        "title": "ЕГЭ Профиль Математика 2026",
        "standard": "ЕГЭ Профиль",
        "language": "ru",
        "status": "active",
        "nodes": [
            # --- Задание 4 (Б): базовая вероятность ---
            {"order": 1,  "uid": "TOP-VEROYATNOST-d3cd07",                                 "task": "4"},
            {"order": 2,  "uid": "TOP-OSNOVY-TEORII-VEROYATNOS-c8e176",                    "task": "4"},
            # --- Задание 5 (П): комбинаторика, формулы сложения/умножения ---
            {"order": 3,  "uid": "TOP-9-ELEMENTY-KOMBINATORIKI",                           "task": "5"},
            {"order": 4,  "uid": "TOP-11-KOMBINATORIKA-I-BINOM-NYUTONA",                   "task": "5"},
            # --- Задание 6 (Б): уравнения и системы базового уровня ---
            {"order": 5,  "uid": "TOP-KVADRATNYE-URAVNENIYA-0fdb01",                       "task": "6"},
            {"order": 6,  "uid": "TOP-7-SISTEMY-LINEJNYH-URAVNENIJ",                       "task": "6"},
            {"order": 7,  "uid": "TOP-8-SISTEMY-LINEJNYH-URAVNENIJ-S-DVUMYA-PEREMENNYMI-20260322", "task": "6"},
            {"order": 8,  "uid": "TOP-10-RAVNOSILNYE-UR-I-NER",                            "task": "6,15"},
            # --- Задание 7 (Б): степени, корни, логарифмы — вычисления ---
            {"order": 9,  "uid": "TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM",                 "task": "7"},
            {"order": 10, "uid": "TOP-KORNEVYE-FUNKTSII-2a9a47",                           "task": "7"},
            {"order": 11, "uid": "TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea",                   "task": "7"},
            {"order": 12, "uid": "TOP-10-POKAZATELNAYA-FUNKCIYA",                          "task": "7,15"},
            # --- Задание 8 (Б): производная и интеграл ---
            {"order": 13, "uid": "TOP-PRAVILA-DIFFERENTSIROVANIYA-3bd912",                 "task": "8,12"},
            {"order": 14, "uid": "TOP-PROIZVODNAYA-cfd26d",                                "task": "8"},
            {"order": 15, "uid": "TOP-11-GEOMETRICHESKIJ-SMYSL-PROIZVODNOJ",               "task": "8"},
            # --- Задание 10 (П): текстовые задачи ---
            {"order": 16, "uid": "TOP-TEKSTOVYE-ZADACHI-004",                              "task": "9,10"},
            # --- Задания 11 (П): свойства и графики функций ---
            {"order": 17, "uid": "TOP-9-FUNKCII-I-IX-SVOYSTVA",                            "task": "11"},
            {"order": 18, "uid": "TOP-9-KVADRATICHNAYA-FUNKCIYA-I-GRAFIK",                 "task": "11"},
            {"order": 19, "uid": "TOP-STEPENNAYA-FUNKCIYA-9-10",                           "task": "11"},
            {"order": 20, "uid": "TOP-OBRATNAYA-FUNKCIYA-9-10",                            "task": "11"},
            # --- Задание 12 (П): исследование функции через производную ---
            {"order": 21, "uid": "TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f",                       "task": "11,12"},
            # --- Задание 13 (П): тригонометрические уравнения ---
            {"order": 22, "uid": "TOP-RADIANNAYA-MERA-51263f",                             "task": "13"},
            {"order": 23, "uid": "TOP-10-TRIGONOMETRICHESKIE-FORMULY",                     "task": "13"},
            {"order": 24, "uid": "TOP-TRIGONOMETRICHESKIE-FUNKTSII-84c00c",                "task": "13"},
            {"order": 25, "uid": "TOP-10-TRIG-URAVNENIYA-I-NERAVENSTVA",                   "task": "13"},
            {"order": 26, "uid": "TOP-TRIGONOMETRICHESKIE-NERAVENSTV-a65a77",              "task": "13"},
            {"order": 27, "uid": "TOP-TRIGONOMETRICHESKIE-URAVNENIYA-37c238",              "task": "13"},
            # --- Первообразная и интеграл (смежны с заданиями 8, 12) ---
            {"order": 28, "uid": "TOP-PERVOOBRAZNAYA-e23096",                              "task": None},
            {"order": 29, "uid": "TOP-OPREDELYONNYJ-INTEGRAL-2f73d5",                      "task": None},
            {"order": 30, "uid": "TOP-PRIMENENIYA-INTEGRALA-d4e675",                       "task": None},
            # --- Задание 15 (П): показательные/логарифмические/иррациональные ур. и нер. ---
            {"order": 31, "uid": "TOP-10-POKAZATELNYE-URAVNENIYA",                         "task": "15"},
            {"order": 32, "uid": "TOP-10-POKAZATELNYE-NERAVENSTVA",                        "task": "15"},
            {"order": 33, "uid": "TOP-IRRATSIONALNYE-URAVNENIYA-e5dde5",                   "task": "15"},
            {"order": 34, "uid": "TOP-IRRATSIONALNYE-NERAVENSTVA",                         "task": "15"},
            {"order": 35, "uid": "TOP-LOGARIFMICHESKIE-NERAVENSTVA",                       "task": "15"},
            {"order": 36, "uid": "TOP-NERAVENSTVA-S-DVUMYA-PEREMENNYMI",                   "task": "15"},
            # --- Задание 16 (П): финансово-экономические задачи ---
            {"order": 37, "uid": "TOP-MATH-FINANCIAL-ADVANCED",                            "task": "16"},
            # --- Задание 18 (В): задачи с параметром ---
            {"order": 38, "uid": "TOP-EGE-ZADACHI-S-PARAMETROM-2026",                      "task": "18"},
            # --- Задание 19 (В): теория чисел, делимость ---
            {"order": 39, "uid": "TOP-EGE-TEORIYA-CHISEL-DELIMOST-2026",                   "task": "19"},
            # --- Геометрия (задания 1, 2, 3, 14, 17) — заглушки до появления в БЗ ---
            {"order": 40, "uid": "TOP-MATH-PLANE-GEOMETRY",                                "task": "1"},
            {"order": 41, "uid": "TOP-VEKTORY-78d40c",                                     "task": "2"},
            {"order": 42, "uid": "TOP-MATH-STEREOMETRY",                                   "task": "3"},
            {"order": 43, "uid": "TOP-MATH-STEREOMETRY-ADVANCED",                          "task": "14"},
            {"order": 44, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF",                     "task": "17"},
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
