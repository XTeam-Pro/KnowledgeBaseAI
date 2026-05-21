#!/usr/bin/env python3
"""
Migrate OGE/EGE exam-specific Topic nodes to canonical cross-curriculum Topic nodes.

Проблема: в Neo4j существуют тавтологичные топики с разными uid:
    TOP-OGE-VEROYATNOST-I-STATISTIKA-2026  ≡  TOP-EGE-BASE-VEROYATNOST-STAT-2026
    TOP-OGE-GEOMETRIYA-VYCHISLENIE-2026    ≡  TOP-EGE-BASE-PLANIMETRIYA-2026  ≡  TOP-EGE-PROF-PLANIMETRIYA-BASE-2026
    ...

Решение: перевести все топики на 25 канонических uid вида TOP-MATH-*.
    - Создать/обновить канонические Topic-узлы
    - Переподключить рёбра REQUIRES_SKILL от старых узлов к каноническим
    - Переподключить рёбра PREREQ (если есть)
    - Удалить осиротевшие старые узлы

Использование (внутри контейнера):
    python /app/scripts/migrate_to_canonical_topics.py [--dry-run]

Скрипт идемпотентен: повторный запуск безопасен.
"""

import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graph.neo4j_repo import Neo4jRepo  # noqa: E402

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

# ---------------------------------------------------------------------------
# Канонические топики: 25 узлов Topic
# ---------------------------------------------------------------------------
# Формат: uid → {title, description, difficulty_level, difficulty_band,
#                user_class_min, user_class_max}
CANONICAL_TOPICS = {
    # ── Shared OGE + EGE (merged) ──────────────────────────────────────────
    "TOP-MATH-EQUATIONS-SYSTEMS": {
        "title": "Уравнения, системы уравнений и неравенства",
        "description": (
            "Линейные и квадратные уравнения, системы уравнений, "
            "линейные и квадратные неравенства — от ОГЭ до ЕГЭ базового уровня."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 9,
        "user_class_max": 11,
    },
    "TOP-MATH-PLANE-GEOMETRY": {
        "title": "Планиметрия: вычислительные задачи",
        "description": (
            "Вычисление углов, длин, площадей плоских фигур. "
            "Теоремы Пифагора, косинусов, синусов; подобие треугольников; "
            "окружность и вписанные фигуры — ОГЭ и ЕГЭ базовый/профиль."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 9,
        "user_class_max": 11,
    },
    "TOP-MATH-FUNCTIONS-GRAPHS": {
        "title": "Функции, их свойства и графики",
        "description": (
            "Линейная, квадратичная, обратная пропорциональность; "
            "чтение и построение графиков; координатный метод; "
            "показательная и логарифмическая (базовый уровень)."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 9,
        "user_class_max": 11,
    },
    "TOP-MATH-PROBABILITY-STATISTICS": {
        "title": "Теория вероятностей и статистика",
        "description": (
            "Классическая вероятность, правила сложения и умножения, "
            "среднее, медиана, мода; чтение таблиц и диаграмм — ОГЭ и ЕГЭ."
        ),
        "difficulty_level": 3,
        "difficulty_band": "basic",
        "user_class_min": 9,
        "user_class_max": 11,
    },
    "TOP-MATH-APPLIED-MATH": {
        "title": "Прикладная математика: практические задачи",
        "description": (
            "Многошаговые задачи из реальной жизни — кредиты, вклады, налоги, "
            "тарифы, оптимальный выбор; проценты, единицы измерения, масштаб."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 9,
        "user_class_max": 11,
    },

    # ── OGE-specific ────────────────────────────────────────────────────────
    "TOP-MATH-ALGEBRA-TRANSFORMS": {
        "title": "Алгебраические преобразования",
        "description": (
            "Упрощение алгебраических выражений: раскрытие скобок, "
            "формулы сокращённого умножения, преобразование дробей."
        ),
        "difficulty_level": 3,
        "difficulty_band": "basic",
        "user_class_min": 9,
        "user_class_max": 9,
    },
    "TOP-MATH-INEQUALITIES": {
        "title": "Неравенства и системы неравенств",
        "description": (
            "Линейные и квадратные неравенства, системы неравенств, "
            "числовая прямая — ОГЭ уровень."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 9,
        "user_class_max": 9,
    },
    "TOP-MATH-PROGRESSIONS": {
        "title": "Числовые последовательности и прогрессии",
        "description": (
            "Арифметическая и геометрическая прогрессии: "
            "n-й член и сумма n первых членов."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 9,
        "user_class_max": 9,
    },
    "TOP-MATH-ADVANCED-ALGEBRA": {
        "title": "Алгебра: задачи повышенного уровня",
        "description": (
            "Дробно-рациональные уравнения, системы с квадратными уравнениями, "
            "параметрические задачи — ОГЭ, часть 2."
        ),
        "difficulty_level": 7,
        "difficulty_band": "advanced",
        "user_class_min": 9,
        "user_class_max": 9,
    },
    "TOP-MATH-ADVANCED-PLANE-GEOM": {
        "title": "Геометрия: задачи повышенного уровня",
        "description": (
            "Вписанные и центральные углы, подобие треугольников, "
            "доказательства — ОГЭ, часть 2."
        ),
        "difficulty_level": 7,
        "difficulty_band": "advanced",
        "user_class_min": 9,
        "user_class_max": 9,
    },
    "TOP-MATH-ADVANCED-FUNCTIONS": {
        "title": "Функции: задачи повышенного уровня",
        "description": (
            "Исследование функций, задачи с параметром, "
            "графический метод — ОГЭ, часть 2."
        ),
        "difficulty_level": 8,
        "difficulty_band": "advanced",
        "user_class_min": 9,
        "user_class_max": 9,
    },

    # ── EGE Base-specific ───────────────────────────────────────────────────
    "TOP-MATH-NUMBERS-CALCULATIONS": {
        "title": "Числа и практические вычисления",
        "description": (
            "Вычисления с натуральными, дробными и десятичными числами, "
            "степени, корни, проценты — ЕГЭ базовый."
        ),
        "difficulty_level": 2,
        "difficulty_band": "basic",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-DERIVATIVES": {
        "title": "Производная и её применение",
        "description": (
            "Нахождение производной, исследование функции на монотонность и экстремумы, "
            "наибольшее и наименьшее значение — ЕГЭ базовый."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-STEREOMETRY": {
        "title": "Стереометрия: объёмы и площади",
        "description": (
            "Объёмы и площади поверхностей призм, цилиндров, конусов, пирамид, шаров — "
            "ЕГЭ базовый."
        ),
        "difficulty_level": 4,
        "difficulty_band": "standard",
        "user_class_min": 11,
        "user_class_max": 11,
    },

    # ── EGE Profile-specific ────────────────────────────────────────────────
    "TOP-MATH-TRIGONOMETRY": {
        "title": "Тригонометрия",
        "description": (
            "Тригонометрические функции, формулы приведения, основное тождество, "
            "значения на единичной окружности, тригонометрические уравнения — ЕГЭ профиль."
        ),
        "difficulty_level": 6,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-EXP-LOG": {
        "title": "Показательные и логарифмические функции",
        "description": (
            "Показательные и логарифмические уравнения и неравенства, "
            "ОДЗ, замена переменной — ЕГЭ профиль."
        ),
        "difficulty_level": 6,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-CALCULUS": {
        "title": "Производная и интеграл (профиль)",
        "description": (
            "Производная сложной функции, первообразные, "
            "вычисление определённых интегралов — ЕГЭ профиль."
        ),
        "difficulty_level": 7,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-ADVANCED-TRIG": {
        "title": "Тригонометрические уравнения: сложные случаи",
        "description": (
            "Однородные тригонометрические уравнения, замена переменной, "
            "отбор корней на промежутке — ЕГЭ профиль, часть 2."
        ),
        "difficulty_level": 8,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-STEREOMETRY-ADVANCED": {
        "title": "Стереометрия: расстояния и углы",
        "description": (
            "Координатный метод в пространстве, расстояния, углы, сечения "
            "многогранников — ЕГЭ профиль, часть 2."
        ),
        "difficulty_level": 8,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-FINANCIAL-ADVANCED": {
        "title": "Финансово-экономические расчёты (профиль)",
        "description": (
            "Аннуитетный кредит, вклады с капитализацией, NPV, "
            "сравнение финансовых вариантов — ЕГЭ профиль, часть 2."
        ),
        "difficulty_level": 8,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF": {
        "title": "Планиметрия: доказательство и вычисление",
        "description": (
            "Доказательства, вписанные окружности, углы, дополнительные построения — "
            "ЕГЭ профиль, часть 2."
        ),
        "difficulty_level": 9,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-OPTIMIZATION": {
        "title": "Производная: оптимизация",
        "description": (
            "Наибольшее/наименьшее значение функции на отрезке, "
            "прикладные задачи на оптимизацию — ЕГЭ профиль, часть 2."
        ),
        "difficulty_level": 8,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-NUMBER-THEORY": {
        "title": "Диофантовы уравнения и целочисленные задачи",
        "description": (
            "Метод остатков, модульная арифметика, целочисленные решения уравнений, "
            "признаки делимости — ЕГЭ профиль, часть 2."
        ),
        "difficulty_level": 9,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-COMPLEX-INEQUALITIES": {
        "title": "Иррациональные и трансцендентные неравенства",
        "description": (
            "Иррациональные, показательные, логарифмические, тригонометрические "
            "неравенства и их системы — ЕГЭ профиль, часть 2."
        ),
        "difficulty_level": 8,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
    "TOP-MATH-COMBINATORICS": {
        "title": "Комбинаторика и вероятность (профиль)",
        "description": (
            "Перестановки, сочетания, размещения; формула Бернулли, "
            "геометрическая и условная вероятность — ЕГЭ профиль."
        ),
        "difficulty_level": 6,
        "difficulty_band": "advanced",
        "user_class_min": 11,
        "user_class_max": 11,
    },
}

# ---------------------------------------------------------------------------
# Маппинг: старый uid → канонический uid
# ---------------------------------------------------------------------------
OLD_TO_CANONICAL = {
    # ОГЭ
    "TOP-OGE-ALGEBRAICHESKIE-PREOBRAZOVANIYA-2026": "TOP-MATH-ALGEBRA-TRANSFORMS",
    "TOP-OGE-URAVNENIYA-I-SISTEMY-2026":            "TOP-MATH-EQUATIONS-SYSTEMS",
    "TOP-OGE-NERAVENSTVA-2026":                     "TOP-MATH-INEQUALITIES",
    "TOP-OGE-PROGRESSII-2026":                      "TOP-MATH-PROGRESSIONS",
    "TOP-OGE-GEOMETRIYA-VYCHISLENIE-2026":          "TOP-MATH-PLANE-GEOMETRY",
    "TOP-OGE-KOORDINATNYJ-METOD-2026":              "TOP-MATH-FUNCTIONS-GRAPHS",
    "TOP-OGE-FUNKTSII-SVOJSTVA-2026":               "TOP-MATH-FUNCTIONS-GRAPHS",
    "TOP-OGE-VEROYATNOST-I-STATISTIKA-2026":        "TOP-MATH-PROBABILITY-STATISTICS",
    "TOP-OGE-REALNAYA-MATEMATIKA-2026":             "TOP-MATH-APPLIED-MATH",
    "TOP-OGE-ALGEBRA-CHAST2-2026":                  "TOP-MATH-ADVANCED-ALGEBRA",
    "TOP-OGE-GEOMETRIYA-CHAST2-2026":               "TOP-MATH-ADVANCED-PLANE-GEOM",
    "TOP-OGE-FUNKTSII-CHAST2-2026":                 "TOP-MATH-ADVANCED-FUNCTIONS",
    # ЕГЭ Базовый
    "TOP-EGE-BASE-VYCHISLENIYA-2026":               "TOP-MATH-NUMBERS-CALCULATIONS",
    "TOP-EGE-BASE-URAVNENIYA-NERAVEN-2026":         "TOP-MATH-EQUATIONS-SYSTEMS",
    "TOP-EGE-BASE-FUNKTSII-GRAFIKI-2026":           "TOP-MATH-FUNCTIONS-GRAPHS",
    "TOP-EGE-BASE-PROIZVODNAYA-2026":               "TOP-MATH-DERIVATIVES",
    "TOP-EGE-BASE-PLANIMETRIYA-2026":               "TOP-MATH-PLANE-GEOMETRY",
    "TOP-EGE-BASE-STEREOMETRIYA-2026":              "TOP-MATH-STEREOMETRY",
    "TOP-EGE-BASE-VEROYATNOST-STAT-2026":           "TOP-MATH-PROBABILITY-STATISTICS",
    "TOP-EGE-BASE-VKLADY-KREDITY-2026":             "TOP-MATH-APPLIED-MATH",
    "TOP-EGE-BASE-REALNYE-ZADACHI-2026":            "TOP-MATH-APPLIED-MATH",
    # ЕГЭ Профиль
    "TOP-EGE-PROF-TRIGONOMETRIYA-2026":             "TOP-MATH-TRIGONOMETRY",
    "TOP-EGE-PROF-POKAZATELN-LOGARIFMY-2026":       "TOP-MATH-EXP-LOG",
    "TOP-EGE-PROF-PROIZVODNAYA-INTEGRAL-2026":      "TOP-MATH-CALCULUS",
    "TOP-EGE-PROF-PLANIMETRIYA-BASE-2026":          "TOP-MATH-PLANE-GEOMETRY",
    "TOP-EGE-PROF-TRIG-URAV-SLOZH-2026":            "TOP-MATH-ADVANCED-TRIG",
    "TOP-EGE-PROF-STEREO-SLOZH-2026":               "TOP-MATH-STEREOMETRY-ADVANCED",
    "TOP-EGE-PROF-EKONOMIKA-SLOZH-2026":            "TOP-MATH-FINANCIAL-ADVANCED",
    "TOP-EGE-PROF-PLANIMETRIYA-SLOZH-2026":         "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF",
    "TOP-EGE-PROF-OPTIMIZATSIYA-2026":              "TOP-MATH-OPTIMIZATION",
    "TOP-EGE-PROF-DIOOFANT-TSELYE-2026":            "TOP-MATH-NUMBER-THEORY",
    "TOP-EGE-PROF-NERAVEN-SLOZH-2026":              "TOP-MATH-COMPLEX-INEQUALITIES",
    "TOP-EGE-PROF-KOMBINATORIKA-2026":              "TOP-MATH-COMBINATORICS",
}

# ---------------------------------------------------------------------------
# Граф зависимостей (PREREQ): canonical_uid → [prereqs]
# Обеспечивает правильный порядок изучения тем.
# ---------------------------------------------------------------------------
PREREQ_GRAPH = {
    # ОГЭ/базовые зависимости
    "TOP-MATH-EQUATIONS-SYSTEMS":    ["TOP-MATH-ALGEBRA-TRANSFORMS"],
    "TOP-MATH-INEQUALITIES":         ["TOP-MATH-ALGEBRA-TRANSFORMS"],
    "TOP-MATH-FUNCTIONS-GRAPHS":     ["TOP-MATH-EQUATIONS-SYSTEMS", "TOP-MATH-ALGEBRA-TRANSFORMS"],
    "TOP-MATH-PROBABILITY-STATISTICS": [],
    "TOP-MATH-APPLIED-MATH":         ["TOP-MATH-EQUATIONS-SYSTEMS"],
    "TOP-MATH-PROGRESSIONS":         ["TOP-MATH-EQUATIONS-SYSTEMS"],
    "TOP-MATH-ADVANCED-ALGEBRA":     ["TOP-MATH-EQUATIONS-SYSTEMS", "TOP-MATH-FUNCTIONS-GRAPHS"],
    "TOP-MATH-ADVANCED-PLANE-GEOM":  ["TOP-MATH-PLANE-GEOMETRY"],
    "TOP-MATH-ADVANCED-FUNCTIONS":   ["TOP-MATH-FUNCTIONS-GRAPHS"],
    # ЕГЭ базовые зависимости
    "TOP-MATH-DERIVATIVES":          ["TOP-MATH-FUNCTIONS-GRAPHS"],
    "TOP-MATH-STEREOMETRY":          ["TOP-MATH-PLANE-GEOMETRY"],
    # ЕГЭ профиль зависимости
    "TOP-MATH-TRIGONOMETRY":         ["TOP-MATH-EQUATIONS-SYSTEMS", "TOP-MATH-FUNCTIONS-GRAPHS"],
    "TOP-MATH-EXP-LOG":              ["TOP-MATH-FUNCTIONS-GRAPHS"],
    "TOP-MATH-CALCULUS":             ["TOP-MATH-DERIVATIVES", "TOP-MATH-EXP-LOG"],
    "TOP-MATH-ADVANCED-TRIG":        ["TOP-MATH-TRIGONOMETRY"],
    "TOP-MATH-STEREOMETRY-ADVANCED": ["TOP-MATH-STEREOMETRY"],
    "TOP-MATH-FINANCIAL-ADVANCED":   ["TOP-MATH-APPLIED-MATH"],
    "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF": ["TOP-MATH-PLANE-GEOMETRY", "TOP-MATH-TRIGONOMETRY"],
    "TOP-MATH-OPTIMIZATION":         ["TOP-MATH-CALCULUS"],
    "TOP-MATH-NUMBER-THEORY":        ["TOP-MATH-EQUATIONS-SYSTEMS"],
    "TOP-MATH-COMPLEX-INEQUALITIES": ["TOP-MATH-INEQUALITIES", "TOP-MATH-EXP-LOG"],
    "TOP-MATH-COMBINATORICS":        ["TOP-MATH-PROBABILITY-STATISTICS"],
}


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _merge_canonical_node(session, canonical_uid: str, dry_run: bool) -> None:
    props = CANONICAL_TOPICS[canonical_uid]
    all_props = {
        "uid": canonical_uid,
        "type": "Topic",
        "tenant_id": TENANT_ID,
        "lifecycle_status": "ACTIVE",
        "updated_at": NOW_MS,
        **props,
    }
    if not dry_run:
        session.run(
            "MERGE (n:Topic {uid: $uid, tenant_id: $tid}) SET n += $props",
            uid=canonical_uid, tid=TENANT_ID, props=all_props,
        )
    print(f"  [MERGE Topic] {canonical_uid}: {props['title']}")


def _rewire_skills(session, old_uid: str, new_uid: str, dry_run: bool) -> int:
    """Move REQUIRES_SKILL edges from old_uid to new_uid (avoiding duplicates)."""
    if old_uid == new_uid:
        return 0
    count = 0
    if not dry_run:
        # Find skills connected to old topic but NOT yet connected to canonical
        result = session.run(
            """
            MATCH (old:Topic {uid: $old, tenant_id: $tid})-[:REQUIRES_SKILL]->(s:Skill)
            WHERE NOT EXISTS {
                MATCH (:Topic {uid: $new, tenant_id: $tid})-[:REQUIRES_SKILL]->(s)
            }
            MATCH (canon:Topic {uid: $new, tenant_id: $tid})
            MERGE (canon)-[:REQUIRES_SKILL]->(s)
            RETURN count(s) AS cnt
            """,
            old=old_uid, new=new_uid, tid=TENANT_ID,
        ).single()
        count = result["cnt"] if result else 0
    else:
        result = session.run(
            "MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[:REQUIRES_SKILL]->(s) RETURN count(s) AS cnt",
            uid=old_uid, tid=TENANT_ID,
        ).single()
        count = result["cnt"] if result else 0
    return count


def _rewire_prereqs(session, old_uid: str, new_uid: str, dry_run: bool) -> int:
    """Redirect PREREQ edges from/to old_uid → new_uid."""
    if old_uid == new_uid:
        return 0
    count = 0
    if not dry_run:
        # Outgoing: old→X  become  new→X
        r1 = session.run(
            """
            MATCH (old:Topic {uid: $old, tenant_id: $tid})-[:PREREQ]->(target:Topic)
            WHERE target.uid <> $new
            MATCH (canon:Topic {uid: $new, tenant_id: $tid})
            MERGE (canon)-[:PREREQ]->(target)
            RETURN count(target) AS cnt
            """,
            old=old_uid, new=new_uid, tid=TENANT_ID,
        ).single()
        count += r1["cnt"] if r1 else 0
        # Incoming: X→old  become  X→new
        r2 = session.run(
            """
            MATCH (source:Topic)-[:PREREQ]->(old:Topic {uid: $old, tenant_id: $tid})
            WHERE source.uid <> $new
            MATCH (canon:Topic {uid: $new, tenant_id: $tid})
            MERGE (source)-[:PREREQ]->(canon)
            RETURN count(source) AS cnt
            """,
            old=old_uid, new=new_uid, tid=TENANT_ID,
        ).single()
        count += r2["cnt"] if r2 else 0
    return count


def _delete_old_node(session, old_uid: str, dry_run: bool) -> None:
    """Delete orphaned old Topic node (detach all remaining relationships)."""
    if not dry_run:
        session.run(
            "MATCH (t:Topic {uid: $uid, tenant_id: $tid}) DETACH DELETE t",
            uid=old_uid, tid=TENANT_ID,
        )
    print(f"  [DELETE Topic] {old_uid}")


def _create_prereq_edges(session, dry_run: bool) -> int:
    """Create PREREQ edges between canonical topics as defined in PREREQ_GRAPH."""
    count = 0
    for topic_uid, prereq_uids in PREREQ_GRAPH.items():
        for prereq_uid in prereq_uids:
            if not dry_run:
                session.run(
                    """
                    MATCH (t:Topic {uid: $tuid, tenant_id: $tid})
                    MATCH (p:Topic {uid: $puid, tenant_id: $tid})
                    MERGE (t)-[:PREREQ]->(p)
                    """,
                    tuid=topic_uid, puid=prereq_uid, tid=TENANT_ID,
                )
            count += 1
            print(f"  [PREREQ] {topic_uid} → {prereq_uid}")
    return count


# ---------------------------------------------------------------------------
# Обновление canonical_uid в PostgreSQL
# ---------------------------------------------------------------------------

def _update_postgres_canonical_uids(dry_run: bool) -> int:
    """Update curriculum_nodes.canonical_uid in PostgreSQL to use canonical UIDs."""
    try:
        import psycopg2  # noqa
        from app.config.settings import settings
        dsn = str(settings.pg_dsn) if settings.pg_dsn else ""
        if not dsn:
            print("  [WARN] PostgreSQL not configured — skipping DB update")
            return 0
        conn = psycopg2.connect(dsn)
        updated = 0
        with conn:
            with conn.cursor() as cur:
                for old_uid, new_uid in OLD_TO_CANONICAL.items():
                    if old_uid == new_uid:
                        continue
                    if not dry_run:
                        cur.execute(
                            "UPDATE curriculum_nodes SET canonical_uid = %s WHERE canonical_uid = %s",
                            (new_uid, old_uid),
                        )
                        updated += cur.rowcount
                    else:
                        cur.execute(
                            "SELECT count(*) FROM curriculum_nodes WHERE canonical_uid = %s",
                            (old_uid,),
                        )
                        n = cur.fetchone()[0]
                        if n:
                            print(f"  [DRY] PG: would update {n} rows: {old_uid} → {new_uid}")
                            updated += n
        conn.close()
        return updated
    except Exception as exc:
        print(f"  [WARN] PostgreSQL update failed: {exc}")
        return 0


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

def migrate(dry_run: bool = False) -> None:
    repo = Neo4jRepo()
    drv = repo.driver

    topics_created = 0
    skills_rewired = 0
    prereqs_rewired = 0
    topics_deleted = 0

    try:
        with drv.session() as session:
            # 1. Create / update canonical topic nodes
            print("─" * 60)
            print("Шаг 1: Создание/обновление канонических Topic-узлов")
            print("─" * 60)
            for canonical_uid in CANONICAL_TOPICS:
                _merge_canonical_node(session, canonical_uid, dry_run)
                topics_created += 1

            # 2. Rewire REQUIRES_SKILL and PREREQ from old → canonical
            print()
            print("─" * 60)
            print("Шаг 2: Перенаправление рёбер REQUIRES_SKILL и PREREQ")
            print("─" * 60)
            for old_uid, new_uid in OLD_TO_CANONICAL.items():
                if old_uid == new_uid:
                    continue
                n_skills = _rewire_skills(session, old_uid, new_uid, dry_run)
                n_prereqs = _rewire_prereqs(session, old_uid, new_uid, dry_run)
                skills_rewired += n_skills
                prereqs_rewired += n_prereqs
                if n_skills or n_prereqs:
                    mode = "DRY" if dry_run else "DONE"
                    print(f"  [{mode}] {old_uid} → {new_uid}: {n_skills} skills, {n_prereqs} prereqs")

            # 3. Create canonical PREREQ edges
            print()
            print("─" * 60)
            print("Шаг 3: Создание PREREQ-рёбер между каноническими топиками")
            print("─" * 60)
            n_prereq_edges = _create_prereq_edges(session, dry_run)

            # 4. Delete orphaned old topic nodes
            print()
            print("─" * 60)
            print("Шаг 4: Удаление устаревших Topic-узлов")
            print("─" * 60)
            deleted_uids: set = set()
            for old_uid, new_uid in OLD_TO_CANONICAL.items():
                if old_uid == new_uid:
                    continue
                if old_uid not in deleted_uids:
                    _delete_old_node(session, old_uid, dry_run)
                    deleted_uids.add(old_uid)
                    topics_deleted += 1

    finally:
        repo.close()

    # 5. Update PostgreSQL curriculum_nodes
    print()
    print("─" * 60)
    print("Шаг 5: Обновление canonical_uid в PostgreSQL")
    print("─" * 60)
    pg_updated = _update_postgres_canonical_uids(dry_run)
    if pg_updated:
        print(f"  {'[DRY]' if dry_run else '[DONE]'} обновлено {pg_updated} записей в curriculum_nodes")

    mode = "(DRY RUN)" if dry_run else "(APPLIED)"
    print()
    print(f"{'=' * 60}")
    print(f"Миграция завершена {mode}")
    print(f"  Canonical topics created/updated : {topics_created}")
    print(f"  Skills rewired                   : {skills_rewired}")
    print(f"  PREREQ edges rewired             : {prereqs_rewired}")
    print(f"  PREREQ canonical edges created   : {n_prereq_edges}")
    print(f"  Old topic nodes deleted          : {topics_deleted}")
    print(f"  PostgreSQL rows updated          : {pg_updated}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate OGE/EGE topics to canonical UIDs")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    print("Migrate: OGE/EGE топики → канонические uid")
    print(f"Режим: {'DRY RUN' if args.dry_run else 'WRITE'}")
    print("=" * 60)
    migrate(dry_run=args.dry_run)
