#!/usr/bin/env python3
"""Seed Method + Example nodes with user_class_min / user_class_max.

Creates proposals via the KB proposal API, then commits them.
Each Method node gets a class range (e.g. 5-7) and Examples also get
the same range so that grade-appropriate content is returned.

Content is based on official Russian mathematics textbooks:
  - 1-4 kl: Моро М.И. et al.
  - 5-6 kl: Виленкин Н.Я., Мерзляк А.Г.
  - 7-9 kl: Макарычев Ю.Н., Атанасян Л.С., Мерзляк А.Г.
  - 10-11 kl: Алимов Ш.А., Колмогоров А.Н., Мордкович А.Г.

Usage:
    python scripts/seed_methods_by_grade.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Proposal operations builder
# ---------------------------------------------------------------------------

_OP_COUNTER = 0


def _next_op_id() -> str:
    global _OP_COUNTER
    _OP_COUNTER += 1
    return str(_OP_COUNTER)


def create_node(uid: str, node_type: str, props: dict[str, Any], quote: str = "") -> dict:
    return {
        "op_id": _next_op_id(),
        "op_type": "CREATE_NODE",
        "target_id": uid,
        "properties_delta": {"type": node_type, **props},
        "evidence": {"source_chunk_id": "seed_methods_by_grade", "quote": quote or props.get("title", "")},
    }


def create_rel(from_uid: str, to_uid: str, rel_type: str, quote: str = "") -> dict:
    return {
        "op_id": _next_op_id(),
        "op_type": "CREATE_REL",
        "properties_delta": {"type": rel_type, "from_uid": from_uid, "to_uid": to_uid},
        "evidence": {"source_chunk_id": "seed_methods_by_grade", "quote": quote or f"{from_uid}->{to_uid}"},
    }


# ---------------------------------------------------------------------------
# 1. Вероятности — TOP-MATH-PROBABILITY-STATISTICS (already exists)
#    Need Skill + Methods per grade band + Examples
# ---------------------------------------------------------------------------

def _probability_ops() -> list[dict]:
    ops: list[dict] = []
    topic_uid = "TOP-MATH-PROBABILITY-STATISTICS"
    skill_uid = "SKL-PROBABILITY-STATISTICS"

    ops.append(create_node(skill_uid, "Skill", {
        "title": "Теория вероятностей и статистика",
    }))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    # --- 5-7 класс: Классическая вероятность (Мерзляк 5-6, Макарычев 7) ---
    methods_5_7 = [
        {
            "uid": "MET-PROB-KLASSICH-DEF",
            "title": "Классическое определение вероятности",
            "description": "P(A) = m/n, где m — число благоприятных исходов, n — общее число равновозможных исходов. Учебник: Мерзляк А.Г. 6 кл.",
            "examples": [
                {"uid": "EX-PROB-KOST-1", "title": "Бросок кубика",
                 "statement": "Какова вероятность выпадения чётного числа при бросании игрального кубика?",
                 "solution": "Благоприятные исходы: 2, 4, 6 — всего 3. Общее число исходов: 6. P = 3/6 = 0.5", "difficulty_level": 1},
                {"uid": "EX-PROB-MONETA-1", "title": "Подбрасывание монеты",
                 "statement": "Монету подбрасывают 1 раз. Какова вероятность выпадения орла?",
                 "solution": "Благоприятных исходов: 1 (орёл). Всего исходов: 2. P = 1/2 = 0.5", "difficulty_level": 1},
            ],
        },
        {
            "uid": "MET-PROB-SLUCHAJNYE-SOBITIYA",
            "title": "Достоверные, невозможные и случайные события",
            "description": "Классификация событий: достоверное P=1, невозможное P=0, случайное 0<P<1. Учебник: Макарычев Ю.Н. 7 кл.",
            "examples": [
                {"uid": "EX-PROB-DOSTOV-1", "title": "Определение типа события",
                 "statement": "В мешке 5 красных шаров. Вынимают 1 шар. Событие «шар красный» — какого типа?",
                 "solution": "Все шары красные → событие достоверное, P = 1", "difficulty_level": 1},
                {"uid": "EX-PROB-NEVOZM-1", "title": "Невозможное событие",
                 "statement": "В мешке 5 красных шаров. Событие «вынут синий шар». Какова его вероятность?",
                 "solution": "Синих шаров нет → событие невозможное, P = 0", "difficulty_level": 1},
            ],
        },
        {
            "uid": "MET-PROB-STATISTIKA-CHAST",
            "title": "Статистическая (относительная) частота",
            "description": "Частота события = число наступлений / число опытов. При большом числе опытов частота приближается к вероятности. Учебник: Макарычев Ю.Н. 7 кл.",
            "examples": [
                {"uid": "EX-PROB-STAT-CHAST-1", "title": "Частота попаданий",
                 "statement": "Баскетболист сделал 50 бросков, попал 35 раз. Найдите относительную частоту попадания.",
                 "solution": "W = 35/50 = 0.7", "difficulty_level": 1},
            ],
        },
    ]

    for m in methods_5_7:
        ops.append(create_node(m["uid"], "Method", {
            "title": m["title"],
            "description": m["description"],
            "user_class_min": 5,
            "user_class_max": 7,
        }))
        ops.append(create_rel(skill_uid, m["uid"], "HAS_METHOD"))
        for ex in m.get("examples", []):
            ops.append(create_node(ex["uid"], "Example", {
                "title": ex["title"],
                "statement": ex["statement"],
                "solution": ex["solution"],
                "difficulty_level": ex.get("difficulty_level", 1),
                "user_class_min": 5,
                "user_class_max": 7,
            }))
            ops.append(create_rel(m["uid"], ex["uid"], "HAS_EXAMPLE"))

    # --- 8-9 класс: Комбинаторика и формулы вероятности (Макарычев 9, Мерзляк 9) ---
    methods_8_9 = [
        {
            "uid": "MET-PROB-SLOZHENIE",
            "title": "Теоремы сложения вероятностей",
            "description": "P(A∪B) = P(A) + P(B) для несовместных событий. P(A∪B) = P(A) + P(B) − P(A∩B) для совместных. Учебник: Макарычев Ю.Н. 9 кл.",
            "examples": [
                {"uid": "EX-PROB-SLOZH-1", "title": "Несовместные события",
                 "statement": "В урне 3 белых, 4 чёрных, 2 красных шара. Какова вероятность достать белый или красный шар?",
                 "solution": "P(Б) = 3/9, P(К) = 2/9. События несовместны. P(Б∪К) = 3/9 + 2/9 = 5/9 ≈ 0.556", "difficulty_level": 2},
            ],
        },
        {
            "uid": "MET-PROB-UMNOZHENIE",
            "title": "Теорема умножения вероятностей",
            "description": "P(A∩B) = P(A) · P(B|A). Для независимых: P(A∩B) = P(A) · P(B). Учебник: Мерзляк А.Г. 9 кл.",
            "examples": [
                {"uid": "EX-PROB-UMNOZH-1", "title": "Независимые события",
                 "statement": "Стрелок попадает в мишень с вероятностью 0.8. Какова вероятность двух попаданий подряд?",
                 "solution": "События независимы. P = 0.8 × 0.8 = 0.64", "difficulty_level": 2},
            ],
        },
        {
            "uid": "MET-PROB-KOMBINATORIKA",
            "title": "Комбинаторный подсчёт исходов",
            "description": "Применение правила произведения, перестановок P(n) = n!, размещений A(n,k) = n!/(n-k)!, сочетаний C(n,k) = n!/(k!(n-k)!). Учебник: Макарычев Ю.Н. 9 кл.",
            "examples": [
                {"uid": "EX-PROB-KOMBIN-1", "title": "Сочетания",
                 "statement": "Из 10 учеников выбирают 3 для участия в олимпиаде. Сколькими способами это можно сделать?",
                 "solution": "C(10,3) = 10!/(3!·7!) = (10·9·8)/(3·2·1) = 120", "difficulty_level": 2},
            ],
        },
    ]

    for m in methods_8_9:
        ops.append(create_node(m["uid"], "Method", {
            "title": m["title"],
            "description": m["description"],
            "user_class_min": 8,
            "user_class_max": 9,
        }))
        ops.append(create_rel(skill_uid, m["uid"], "HAS_METHOD"))
        for ex in m.get("examples", []):
            ops.append(create_node(ex["uid"], "Example", {
                "title": ex["title"],
                "statement": ex["statement"],
                "solution": ex["solution"],
                "difficulty_level": ex.get("difficulty_level", 2),
                "user_class_min": 8,
                "user_class_max": 9,
            }))
            ops.append(create_rel(m["uid"], ex["uid"], "HAS_EXAMPLE"))

    # --- 10-11 класс: Формула Бернулли, условная вероятность, Байес (Колмогоров 10-11) ---
    methods_10_11 = [
        {
            "uid": "MET-PROB-BERNOULLI",
            "title": "Формула Бернулли",
            "description": "P(k) = C(n,k) · p^k · q^(n-k), где q = 1-p. Применяется к серии из n независимых испытаний. Учебник: Колмогоров А.Н. 10-11 кл.",
            "examples": [
                {"uid": "EX-PROB-BERN-1", "title": "Серия испытаний",
                 "statement": "Монету подбрасывают 5 раз. Какова вероятность выпадения ровно 3 орлов?",
                 "solution": "P(3) = C(5,3) · (0.5)^3 · (0.5)^2 = 10 · 0.125 · 0.25 = 0.3125", "difficulty_level": 3},
            ],
        },
        {
            "uid": "MET-PROB-USLOVNAYA",
            "title": "Условная вероятность",
            "description": "P(B|A) = P(A∩B)/P(A). Вероятность события B при условии, что произошло событие A. Учебник: Колмогоров А.Н. 10-11 кл.",
            "examples": [
                {"uid": "EX-PROB-USLOVN-1", "title": "Условная вероятность",
                 "statement": "Из колоды 36 карт вынута одна карта — она оказалась красной масти. Какова вероятность, что это бубна?",
                 "solution": "Красных мастей 2 (бубна + черва) по 9 карт = 18. P(бубна|красная) = 9/18 = 0.5", "difficulty_level": 3},
            ],
        },
        {
            "uid": "MET-PROB-BAYES",
            "title": "Формула Байеса",
            "description": "P(H_i|A) = P(H_i)·P(A|H_i) / Σ P(H_j)·P(A|H_j). Пересчёт вероятностей гипотез после наблюдения. Учебник: Колмогоров А.Н. 10-11 кл.",
            "examples": [
                {"uid": "EX-PROB-BAYES-1", "title": "Формула Байеса",
                 "statement": "Завод имеет 2 станка. Станок 1 производит 60% деталей с браком 3%. Станок 2 — 40% с браком 5%. Наугад взятая деталь бракованная. Какова вероятность, что она со станка 1?",
                 "solution": "P(H1)=0.6, P(A|H1)=0.03, P(H2)=0.4, P(A|H2)=0.05. P(A) = 0.6·0.03 + 0.4·0.05 = 0.018+0.02 = 0.038. P(H1|A) = 0.018/0.038 ≈ 0.474", "difficulty_level": 3},
            ],
        },
    ]

    for m in methods_10_11:
        ops.append(create_node(m["uid"], "Method", {
            "title": m["title"],
            "description": m["description"],
            "user_class_min": 10,
            "user_class_max": 11,
        }))
        ops.append(create_rel(skill_uid, m["uid"], "HAS_METHOD"))
        for ex in m.get("examples", []):
            ops.append(create_node(ex["uid"], "Example", {
                "title": ex["title"],
                "statement": ex["statement"],
                "solution": ex["solution"],
                "difficulty_level": ex.get("difficulty_level", 3),
                "user_class_min": 10,
                "user_class_max": 11,
            }))
            ops.append(create_rel(m["uid"], ex["uid"], "HAS_EXAMPLE"))

    return ops


# ---------------------------------------------------------------------------
# 2. User-provided topics: add user_class_min/user_class_max to Methods + Examples
# ---------------------------------------------------------------------------

def _user_topics_ops() -> list[dict]:
    """Build ops from the user's JSON payloads, enriched with grade ranges."""
    ops: list[dict] = []

    # --- Арифметическая прогрессия (9 кл) ---
    sec_uid = "SEC-POSLEDOVATELNOSTI-2026"
    subsec_uid = "SUBSEC-CHISLOVYE-POSLEDOVATELNOSTI-2026"

    ops.append(create_node(sec_uid, "Section", {"title": "Последовательности"}))
    ops.append(create_node(subsec_uid, "Subsection", {"title": "Числовые последовательности"}))
    ops.append(create_rel(sec_uid, subsec_uid, "CONTAINS"))

    # Арифметическая прогрессия
    topic_ap = "TOP-ARIFMETICHESKAYA-PROGRESSIYA-9KL"
    skill_ap = "SKL-ARIFMETICHESKAYA-PROGRESSIYA-9KL"
    ops.append(create_node(topic_ap, "Topic", {"title": "Арифметическая прогрессия", "difficulty_band": "standard", "difficulty_level": 2}))
    ops.append(create_node(skill_ap, "Skill", {"title": "Арифметическая прогрессия"}))
    ops.append(create_rel(subsec_uid, topic_ap, "CONTAINS"))
    ops.append(create_rel(topic_ap, skill_ap, "REQUIRES_SKILL"))

    ap_methods = [
        ("MET-AP-RAZNOST", "Нахождение разности прогрессии", "Разность вычисляется как разница между соседними членами. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-AP-1", "Нахождение разности", "14, 12, 10,... найдите d", "d = 12 - 14 = -2", 1)]),
        ("MET-AP-N-CHLEN", "Нахождение n-го члена", "a_n = a_1 + (n-1)·d. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-AP-2", "Нахождение n-го члена", "a1=9, d=2. Найдите a11", "a11 = 9 + 10×2 = 29", 2)]),
        ("MET-AP-SUMMA", "Нахождение суммы первых n членов", "S_n = n/2 · (2a_1 + (n-1)d) или S_n = n/2 · (a_1 + a_n). Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-AP-3", "Нахождение суммы", "Сумма первых 20 членов 1+2+3+...", "S20 = 20/2 × (2×1 + 19×1) = 210", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in ap_methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_ap, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    # Геометрическая прогрессия
    topic_gp = "TOP-GEOMETRICHESKAYA-PROGRESSIYA-9KL"
    skill_gp = "SKL-GEOMETRICHESKAYA-PROGRESSIYA-9KL"
    ops.append(create_node(topic_gp, "Topic", {"title": "Геометрическая прогрессия", "difficulty_band": "standard", "difficulty_level": 2}))
    ops.append(create_node(skill_gp, "Skill", {"title": "Геометрическая прогрессия"}))
    ops.append(create_rel(subsec_uid, topic_gp, "CONTAINS"))
    ops.append(create_rel(topic_gp, skill_gp, "REQUIRES_SKILL"))

    gp_methods = [
        ("MET-GP-ZNAMENATEL", "Нахождение знаменателя прогрессии", "q = b_(n+1) / b_n. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-GP-1", "Нахождение знаменателя", "2, 6, 18,... найдите q", "q = 6 / 2 = 3", 1)]),
        ("MET-GP-N-CHLEN", "Нахождение n-го члена", "b_n = b_1 · q^(n-1). Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-GP-2", "Нахождение n-го члена", "b1=3, q=2. Найдите b5", "b5 = 3 × 2^4 = 48", 2)]),
        ("MET-GP-SUMMA", "Нахождение суммы первых n членов", "S_n = b_1 · (q^n - 1) / (q - 1). Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-GP-3", "Нахождение суммы", "Сумма первых 4 членов 1, 2, 4, 8", "S4 = 1 × (2^4 - 1)/(2-1) = 15", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in gp_methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_gp, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    # --- Формулы сокращённого умножения (7 кл) ---
    topic_fsu = "TOP-FSU-7KL"
    skill_fsu = "SKL-FSU-7KL"
    ops.append(create_node(topic_fsu, "Topic", {"title": "Формулы сокращённого умножения", "difficulty_band": "standard", "difficulty_level": 2}))
    ops.append(create_node(skill_fsu, "Skill", {"title": "Формулы сокращённого умножения"}))
    ops.append(create_rel("SUBSEC-ALGEBRAICHESKIE-VYRAZHENIYA-ed2415", topic_fsu, "CONTAINS"))
    ops.append(create_rel(topic_fsu, skill_fsu, "REQUIRES_SKILL"))

    fsu_methods = [
        ("MET-FSU-KVADRAT-SUMMY", "Квадрат суммы", "(a+b)² = a² + 2ab + b². Учебник: Макарычев Ю.Н. 7 кл.",
         [("EX-FSU-1", "Квадрат суммы", "Вычислить (3x + 2y)²", "9x² + 12xy + 4y²", 1)]),
        ("MET-FSU-RAZNOST-KVADRATOV", "Разность квадратов", "a² - b² = (a-b)(a+b). Учебник: Макарычев Ю.Н. 7 кл.",
         [("EX-FSU-2", "Разность квадратов", "Разложить 9a² - 16b²", "(3a - 4b)(3a + 4b)", 1)]),
        ("MET-FSU-KUB-SUMMY", "Куб суммы", "(a+b)³ = a³ + 3a²b + 3ab² + b³. Учебник: Макарычев Ю.Н. 7 кл.",
         [("EX-FSU-3", "Куб суммы", "Раскрыть (x + 1)³", "x³ + 3x² + 3x + 1", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in fsu_methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 7, "user_class_max": 7}))
        ops.append(create_rel(skill_fsu, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 7, "user_class_max": 7}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    # --- Проценты (5 кл) ---
    topic_pct = "TOP-PROTSENTY-5KL"
    skill_pct = "SKL-PROTSENTY-5KL"
    ops.append(create_node(topic_pct, "Topic", {"title": "Проценты", "difficulty_band": "easy", "difficulty_level": 1}))
    ops.append(create_node(skill_pct, "Skill", {"title": "Проценты"}))
    ops.append(create_rel("SUBSEC-ARIFMETICHESKAYA-STRUKTURA-909ea5", topic_pct, "CONTAINS"))
    ops.append(create_rel(topic_pct, skill_pct, "REQUIRES_SKILL"))

    pct_methods = [
        ("MET-PROTSENTY-OT-CHISLA", "Нахождение процента от числа", "Число делится на 100 и умножается на количество процентов. Учебник: Виленкин Н.Я. 5 кл.",
         [("EX-PROTSENTY-1", "Нахождение процента от числа", "850 кг, 1% и 3%. Сколько кг каждый?", "1% = 8.5 кг. 3% = 25.5 кг", 1)]),
        ("MET-PROTSENTY-CHISLO-PO", "Нахождение числа по проценту", "Известная часть делится на долю процента. Учебник: Виленкин Н.Я. 5 кл.",
         [("EX-PROTSENTY-2", "Нахождение числа по проценту", "Прочитано 138 стр., это 23% книги. Сколько страниц?", "138 / 0.23 = 600", 1)]),
        ("MET-PROTSENTY-OTNOSHENIE", "Нахождение процентного отношения", "Первое число делится на второе и умножается на 100%. Учебник: Виленкин Н.Я. 5 кл.",
         [("EX-PROTSENTY-3", "Нахождение процентного отношения", "Из 25 учеников 17 без троек. Сколько процентов?", "17/25 × 100% = 68%", 1)]),
    ]
    for m_uid, m_title, m_desc, examples in pct_methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 5, "user_class_max": 5}))
        ops.append(create_rel(skill_pct, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 5, "user_class_max": 5}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


# ---------------------------------------------------------------------------
# 3. Canonical topics: Shared OGE+EGE (grades 9-11)
# ---------------------------------------------------------------------------

def _equations_systems_ops() -> list[dict]:
    """TOP-MATH-EQUATIONS-SYSTEMS — Уравнения, системы уравнений (9-11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-EQUATIONS-SYSTEMS"
    skill_uid = "SKL-EQUATIONS-SYSTEMS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Уравнения и системы уравнений"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    # --- 9 кл: Линейные и квадратные уравнения, системы (Макарычев 7-9) ---
    m9 = [
        ("MET-EQ-KVADR-UR", "Решение квадратных уравнений",
         "ax² + bx + c = 0. Дискриминант D = b² - 4ac. Корни: x = (-b ± √D) / 2a. Учебник: Макарычев Ю.Н. 8 кл.",
         [("EX-EQ-KVADR-1", "Квадратное уравнение", "Решить x² - 5x + 6 = 0",
           "D = 25 - 24 = 1. x₁ = (5+1)/2 = 3, x₂ = (5-1)/2 = 2", 2)]),
        ("MET-EQ-SISTEMA-LIN", "Решение систем линейных уравнений",
         "Метод подстановки и метод сложения. Учебник: Макарычев Ю.Н. 7 кл.",
         [("EX-EQ-SIST-LIN-1", "Система методом подстановки", "Решить: x + y = 5, 2x - y = 1",
           "Из 1-го: y = 5 - x. Подставляем: 2x - (5-x) = 1 → 3x = 6 → x = 2, y = 3", 2)]),
        ("MET-EQ-VIETA", "Теорема Виета",
         "Для x² + px + q = 0: x₁ + x₂ = -p, x₁ · x₂ = q. Учебник: Макарычев Ю.Н. 8 кл.",
         [("EX-EQ-VIETA-1", "Теорема Виета", "По теореме Виета подобрать корни x² - 7x + 12 = 0",
           "x₁ + x₂ = 7, x₁ · x₂ = 12 → x₁ = 3, x₂ = 4", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in m9:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    # --- 10-11 кл: Иррациональные, показательные, логарифмические уравнения (Алимов 10-11) ---
    m11 = [
        ("MET-EQ-IRRATSION", "Иррациональные уравнения",
         "Уединение радикала, возведение обеих частей в степень, проверка корней. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-EQ-IRRATSION-1", "Иррациональное уравнение", "Решить √(x+3) = x - 1",
           "x + 3 = (x-1)² = x² - 2x + 1 → x² - 3x - 2 = 0. D = 17. x₁ = (3+√17)/2 ≈ 3.56. Проверка: √6.56 ≈ 2.56 = 3.56 - 1 ✓", 3)]),
        ("MET-EQ-POKAZAT", "Показательные уравнения",
         "Приведение к одному основанию: aᶠ⁽ˣ⁾ = aᵍ⁽ˣ⁾ → f(x) = g(x). Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-EQ-POKAZAT-1", "Показательное уравнение", "Решить 2^(x+1) = 8",
           "2^(x+1) = 2³ → x + 1 = 3 → x = 2", 2)]),
        ("MET-EQ-LOGARIFM", "Логарифмические уравнения",
         "log_a(f(x)) = b ⟺ f(x) = aᵇ при ОДЗ: f(x) > 0. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-EQ-LOGARIFM-1", "Логарифмическое уравнение", "Решить log₂(x-1) = 3",
           "x - 1 = 2³ = 8 → x = 9. ОДЗ: x - 1 > 0 → x > 1 ✓", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in m11:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 10, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 10, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _plane_geometry_ops() -> list[dict]:
    """TOP-MATH-PLANE-GEOMETRY — Планиметрия (9-11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-PLANE-GEOMETRY"
    skill_uid = "SKL-PLANE-GEOMETRY"

    ops.append(create_node(skill_uid, "Skill", {"title": "Планиметрия: вычислительные задачи"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    # --- 9 кл: Теорема Пифагора, подобие, площади (Атанасян 7-9) ---
    m9 = [
        ("MET-GEOM-PIFAGOR", "Теорема Пифагора",
         "В прямоугольном треугольнике c² = a² + b². Учебник: Атанасян Л.С. 8 кл.",
         [("EX-GEOM-PIF-1", "Теорема Пифагора", "Катеты 3 и 4. Найти гипотенузу.",
           "c = √(9 + 16) = √25 = 5", 1)]),
        ("MET-GEOM-PODOB", "Признаки подобия треугольников",
         "I: два угла равны. II: две стороны пропорциональны и угол между ними равен. III: три стороны пропорциональны. Учебник: Атанасян Л.С. 8 кл.",
         [("EX-GEOM-PODOB-1", "Подобие треугольников", "Треугольники ABC и DEF: ∠A = ∠D = 40°, ∠B = ∠E = 60°. Подобны ли?",
           "Два угла равны → по I признаку подобия △ABC ~ △DEF", 2)]),
        ("MET-GEOM-PLOSHCH-TRIAN", "Площади плоских фигур",
         "S△ = ½ah, S△ = ½ab·sin C, S = πr². Учебник: Атанасян Л.С. 8 кл.",
         [("EX-GEOM-PLOSHCH-1", "Площадь треугольника", "Основание 10, высота 6. Найти площадь.",
           "S = ½ × 10 × 6 = 30", 1)]),
    ]
    for m_uid, m_title, m_desc, examples in m9:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    # --- 10-11 кл: Теоремы косинусов/синусов, вписанные/описанные окружности (Атанасян 7-9, Алимов 10-11) ---
    m11 = [
        ("MET-GEOM-KOSINUS", "Теорема косинусов",
         "c² = a² + b² - 2ab·cos C. Учебник: Атанасян Л.С. 9 кл.",
         [("EX-GEOM-KOS-1", "Теорема косинусов", "a = 5, b = 7, ∠C = 60°. Найти c.",
           "c² = 25 + 49 - 2·5·7·0.5 = 39 → c = √39 ≈ 6.24", 3)]),
        ("MET-GEOM-SINUS", "Теорема синусов",
         "a/sin A = b/sin B = c/sin C = 2R. Учебник: Атанасян Л.С. 9 кл.",
         [("EX-GEOM-SIN-1", "Теорема синусов", "a = 10, ∠A = 30°, ∠B = 45°. Найти b.",
           "10/sin 30° = b/sin 45° → b = 10 · sin 45° / sin 30° = 10 · (√2/2) / 0.5 = 10√2 ≈ 14.14", 3)]),
        ("MET-GEOM-OKRUZHNOST", "Вписанная и описанная окружность",
         "r = S/p (вписанная), R = abc/(4S) (описанная), где p — полупериметр. Учебник: Атанасян Л.С. 9 кл.",
         [("EX-GEOM-VPISANN-1", "Вписанная окружность", "Треугольник со сторонами 3, 4, 5. Найти радиус вписанной окружности.",
           "p = (3+4+5)/2 = 6. S = ½·3·4 = 6. r = 6/6 = 1", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in m11:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 10, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 10, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _functions_graphs_ops() -> list[dict]:
    """TOP-MATH-FUNCTIONS-GRAPHS — Функции и графики (9-11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-FUNCTIONS-GRAPHS"
    skill_uid = "SKL-FUNCTIONS-GRAPHS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Функции, их свойства и графики"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    # --- 9 кл: Линейная, квадратичная, обратная пропорциональность (Макарычев 7-9) ---
    m9 = [
        ("MET-FUNC-LINEJN", "Линейная функция и её график",
         "y = kx + b. k — угловой коэффициент, b — свободный член. График — прямая. Учебник: Макарычев Ю.Н. 7 кл.",
         [("EX-FUNC-LIN-1", "Линейная функция", "Построить график y = 2x - 3. Найти точки пересечения с осями.",
           "При x=0: y = -3. При y=0: x = 1.5. Точки (0, -3) и (1.5, 0)", 1)]),
        ("MET-FUNC-KVADRAT", "Квадратичная функция и парабола",
         "y = ax² + bx + c. Вершина: x₀ = -b/(2a), y₀ = f(x₀). Ось симметрии x = x₀. Учебник: Макарычев Ю.Н. 8 кл.",
         [("EX-FUNC-KVADR-1", "Квадратичная функция", "Найти вершину параболы y = x² - 4x + 3.",
           "x₀ = 4/2 = 2, y₀ = 4 - 8 + 3 = -1. Вершина (2, -1)", 2)]),
        ("MET-FUNC-OBRATN-PROP", "Обратная пропорциональность",
         "y = k/x, k ≠ 0. График — гипербола. Учебник: Макарычев Ю.Н. 8 кл.",
         [("EX-FUNC-OBPR-1", "Обратная пропорциональность", "Для y = 6/x определить, в каких четвертях расположен график.",
           "k = 6 > 0 → график в I и III четвертях", 1)]),
    ]
    for m_uid, m_title, m_desc, examples in m9:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    # --- 10-11 кл: Показательная, логарифмическая функции (Алимов 10-11) ---
    m11 = [
        ("MET-FUNC-POKAZAT", "Показательная функция",
         "y = aˣ, a > 0, a ≠ 1. Область определения — R, область значений — (0, +∞). Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-FUNC-POKAZ-1", "Показательная функция", "Сравнить 3^1.5 и 3^2.",
           "Функция y = 3ˣ возрастающая (a = 3 > 1). 1.5 < 2, значит 3^1.5 < 3^2 = 9", 2)]),
        ("MET-FUNC-LOGARIFM", "Логарифмическая функция",
         "y = log_a(x), a > 0, a ≠ 1. Обратная к показательной. ОДЗ: x > 0. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-FUNC-LOG-1", "Логарифмическая функция", "Найти log₃(81).",
           "3⁴ = 81, значит log₃(81) = 4", 2)]),
        ("MET-FUNC-CHTEN-GRAFIK", "Чтение свойств функции по графику",
         "По графику определить: область определения, область значений, нули, промежутки возрастания/убывания, экстремумы. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-FUNC-CHTGR-1", "Чтение графика", "По графику f(x) с минимумом в (2, -1) и максимумом в (-1, 4) определить промежуток возрастания.",
           "Функция возрастает от минимума к максимуму: на промежутке (2, +∞) или (-∞, -1) в зависимости от поведения", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in m11:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 10, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 10, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _applied_math_ops() -> list[dict]:
    """TOP-MATH-APPLIED-MATH — Прикладная математика (9-11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-APPLIED-MATH"
    skill_uid = "SKL-APPLIED-MATH"

    ops.append(create_node(skill_uid, "Skill", {"title": "Прикладная математика: практические задачи"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    # --- 9 кл: Задачи на проценты, масштаб, единицы (Макарычев, Мерзляк) ---
    m9 = [
        ("MET-APPL-ZADACHA-PROCENT", "Задачи на проценты",
         "Процент от числа, число по проценту, процентное содержание. Учебник: Макарычев Ю.Н. 9 кл. (ОГЭ).",
         [("EX-APPL-PROC-1", "Задача на проценты", "Товар стоил 800 руб., подорожал на 15%. Какова новая цена?",
           "800 × 1.15 = 920 руб.", 1)]),
        ("MET-APPL-GRAFIKI-DIAGRAMMY", "Чтение графиков, таблиц и диаграмм",
         "Извлечение данных из графиков, таблиц; столбчатые и круговые диаграммы. Учебник: Макарычев Ю.Н. 9 кл. (ОГЭ).",
         [("EX-APPL-GRAF-1", "Чтение диаграммы", "По столбчатой диаграмме: январь — 120, февраль — 150, март — 130. Найти среднее.",
           "(120 + 150 + 130) / 3 = 400/3 ≈ 133.3", 1)]),
        ("MET-APPL-MASSHTAB", "Масштаб и практические расчёты",
         "Масштаб 1:1000 означает, что 1 см на карте = 10 м в реальности. Учебник: Мерзляк А.Г. 6 кл.",
         [("EX-APPL-MASSH-1", "Масштаб", "На плане масштаба 1:500 расстояние между зданиями 4 см. Каково реальное расстояние?",
           "4 × 500 = 2000 см = 20 м", 1)]),
    ]
    for m_uid, m_title, m_desc, examples in m9:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    # --- 10-11 кл: Вклады, кредиты, оптимальный выбор (Колмогоров, ЕГЭ база) ---
    m11 = [
        ("MET-APPL-VKLADY", "Вклады и сложные проценты",
         "S = S₀ · (1 + r/100)ⁿ, где S₀ — начальная сумма, r — ставка, n — число периодов. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-APPL-VKLAD-1", "Сложные проценты", "Вклад 100000 руб. под 10% годовых. Сколько через 2 года?",
           "S = 100000 × 1.1² = 100000 × 1.21 = 121000 руб.", 2)]),
        ("MET-APPL-TARIFY", "Задачи на выбор тарифа",
         "Сравнение вариантов: подставить данные в формулы тарифов и выбрать минимальный. ЕГЭ базовый уровень.",
         [("EX-APPL-TARIF-1", "Выбор тарифа", "Тариф A: 500 + 2 руб./мин. Тариф B: 800 + 1 руб./мин. При каком числе минут A дешевле?",
           "500 + 2x < 800 + x → x < 300. Тариф A дешевле при менее 300 минут.", 2)]),
        ("MET-APPL-KREDITY", "Кредитные расчёты",
         "Аннуитетный платёж. Остаток долга после платежа: D_n = D_{n-1}·(1+r) - P. Учебник: ЕГЭ базовый уровень.",
         [("EX-APPL-KREDIT-1", "Аннуитетный кредит", "Кредит 100000 руб. под 12% годовых (1% в месяц), платёж 3000 руб./мес. Долг после 1-го месяца?",
           "D₁ = 100000 × 1.01 - 3000 = 101000 - 3000 = 98000 руб.", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in m11:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 10, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 10, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


# ---------------------------------------------------------------------------
# 4. OGE-specific topics (grade 9 only)
# ---------------------------------------------------------------------------

def _algebra_transforms_ops() -> list[dict]:
    """TOP-MATH-ALGEBRA-TRANSFORMS — Алгебраические преобразования (9 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-ALGEBRA-TRANSFORMS"
    skill_uid = "SKL-ALGEBRA-TRANSFORMS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Алгебраические преобразования"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-ALG-RASKRYTIE-SKOBOK", "Раскрытие скобок и приведение подобных",
         "a(b + c) = ab + ac. Подобные слагаемые — одинаковые буквенные части. Учебник: Макарычев Ю.Н. 7 кл.",
         [("EX-ALG-RASKR-1", "Раскрытие скобок", "Упростить 3(x + 2) - 2(x - 1)",
           "3x + 6 - 2x + 2 = x + 8", 1)]),
        ("MET-ALG-DROBI", "Действия с алгебраическими дробями",
         "Сокращение, сложение, вычитание, умножение и деление дробей. Учебник: Макарычев Ю.Н. 8 кл.",
         [("EX-ALG-DROB-1", "Алгебраическая дробь", "Упростить (x²-4)/(x+2)",
           "(x²-4)/(x+2) = (x-2)(x+2)/(x+2) = x - 2, при x ≠ -2", 2)]),
        ("MET-ALG-RAZLOZHENIE", "Разложение на множители",
         "Вынесение общего множителя, группировка, формулы сокращённого умножения. Учебник: Макарычев Ю.Н. 7 кл.",
         [("EX-ALG-RAZL-1", "Разложение на множители", "Разложить x³ - x",
           "x(x² - 1) = x(x - 1)(x + 1)", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _inequalities_ops() -> list[dict]:
    """TOP-MATH-INEQUALITIES — Неравенства (9 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-INEQUALITIES"
    skill_uid = "SKL-INEQUALITIES"

    ops.append(create_node(skill_uid, "Skill", {"title": "Неравенства и системы неравенств"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-INEQ-LINEJN", "Линейные неравенства",
         "ax + b > 0. При a > 0: x > -b/a. При a < 0: x < -b/a (знак меняется). Учебник: Макарычев Ю.Н. 8 кл.",
         [("EX-INEQ-LIN-1", "Линейное неравенство", "Решить -3x + 6 > 0",
           "-3x > -6 → x < 2 (делим на -3, знак меняется). Ответ: (-∞, 2)", 1)]),
        ("MET-INEQ-KVADRAT", "Квадратные неравенства методом интервалов",
         "ax² + bx + c > 0: найти корни, отметить на оси, расставить знаки. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-INEQ-KVADR-1", "Квадратное неравенство", "Решить x² - 5x + 6 ≤ 0",
           "Корни: x = 2, x = 3. Парабола вверх ∪. Между корнями ≤ 0. Ответ: [2, 3]", 2)]),
        ("MET-INEQ-SISTEMA", "Системы неравенств",
         "Пересечение множеств решений. Решить каждое неравенство отдельно, найти общую часть. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-INEQ-SIST-1", "Система неравенств", "Решить: x + 1 > 0 и 2x - 6 < 0",
           "x > -1 и x < 3. Пересечение: (-1, 3)", 1)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _progressions_ops() -> list[dict]:
    """TOP-MATH-PROGRESSIONS — Прогрессии (9 кл).

    Note: separate from user-provided AP/GP topics which have their own
    non-canonical UIDs. This uses the canonical TOP-MATH-PROGRESSIONS uid.
    """
    ops: list[dict] = []
    topic_uid = "TOP-MATH-PROGRESSIONS"
    skill_uid = "SKL-PROGRESSIONS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Числовые последовательности и прогрессии"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-PROGR-AP-FORMULA", "Формулы арифметической прогрессии",
         "a_n = a₁ + (n-1)d. S_n = n(a₁ + aₙ)/2. Характеристическое свойство: aₙ = (aₙ₋₁ + aₙ₊₁)/2. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-PROGR-AP-1", "Арифметическая прогрессия", "a₁ = 3, d = 5. Найти S₁₀.",
           "a₁₀ = 3 + 9×5 = 48. S₁₀ = 10×(3+48)/2 = 255", 2)]),
        ("MET-PROGR-GP-FORMULA", "Формулы геометрической прогрессии",
         "bₙ = b₁·q^(n-1). Sₙ = b₁(qⁿ-1)/(q-1). Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-PROGR-GP-1", "Геометрическая прогрессия", "b₁ = 2, q = 3. Найти b₅ и S₅.",
           "b₅ = 2·3⁴ = 162. S₅ = 2(3⁵-1)/(3-1) = 2·242/2 = 242", 2)]),
        ("MET-PROGR-SMESHANNYE", "Смешанные задачи на прогрессии",
         "Задачи, в которых нужно определить тип прогрессии и применить формулы. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-PROGR-SMESH-1", "Определение типа прогрессии", "Последовательность: 5, 10, 20, 40,... Какая это прогрессия? Найти 6-й член.",
           "Каждый следующий в 2 раза больше → ГП, q = 2. b₆ = 5·2⁵ = 160", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _advanced_algebra_ops() -> list[dict]:
    """TOP-MATH-ADVANCED-ALGEBRA — Алгебра повышенного уровня (9 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-ADVANCED-ALGEBRA"
    skill_uid = "SKL-ADVANCED-ALGEBRA"

    ops.append(create_node(skill_uid, "Skill", {"title": "Алгебра: задачи повышенного уровня"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-ADV-ALG-DROB-RAC", "Дробно-рациональные уравнения",
         "Привести к общему знаменателю, решить числитель = 0, проверить ОДЗ. Учебник: Макарычев Ю.Н. 8 кл.",
         [("EX-ADV-ALG-DR-1", "Дробно-рациональное уравнение", "Решить 1/(x-1) + 1/(x+1) = 1",
           "ОДЗ: x ≠ ±1. (x+1+x-1)/((x-1)(x+1)) = 1 → 2x = x²-1 → x²-2x-1 = 0. D = 8. x = 1±√2", 3)]),
        ("MET-ADV-ALG-SISTEMA-NELINET", "Системы с нелинейными уравнениями",
         "Подстановка или сложение. Часто одно уравнение линейное, второе квадратное. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-ADV-ALG-SIST-1", "Нелинейная система", "Решить: x + y = 5, xy = 6",
           "y = 5 - x → x(5-x) = 6 → x²-5x+6 = 0 → x = 2, y = 3 или x = 3, y = 2", 3)]),
        ("MET-ADV-ALG-PARAMETR-OGE", "Задачи с параметром (ОГЭ)",
         "Исследование уравнений в зависимости от параметра a. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-ADV-ALG-PAR-1", "Задача с параметром", "При каких a уравнение ax² + 2x - 1 = 0 имеет два корня?",
           "При a ≠ 0: D = 4 + 4a > 0 → a > -1. С учётом a ≠ 0: a ∈ (-1, 0) ∪ (0, +∞)", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _advanced_plane_geom_ops() -> list[dict]:
    """TOP-MATH-ADVANCED-PLANE-GEOM — Геометрия повышенного уровня (9 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-ADVANCED-PLANE-GEOM"
    skill_uid = "SKL-ADVANCED-PLANE-GEOM"

    ops.append(create_node(skill_uid, "Skill", {"title": "Геометрия: задачи повышенного уровня"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-ADV-GEOM-VPISANNYE-UGLY", "Вписанные и центральные углы",
         "Вписанный угол = ½ центрального, опирающегося на ту же дугу. Учебник: Атанасян Л.С. 8 кл.",
         [("EX-ADV-GEOM-VPIS-1", "Вписанный угол", "Центральный угол = 120°. Чему равен вписанный угол, опирающийся на ту же дугу?",
           "Вписанный = 120°/2 = 60°", 2)]),
        ("MET-ADV-GEOM-PODOB-SLOZH", "Подобие в сложных конфигурациях",
         "Задачи с несколькими подобными треугольниками. Учебник: Атанасян Л.С. 8 кл.",
         [("EX-ADV-GEOM-POD-1", "Подобие", "В △ABC проведена высота BH к AC. AB = 6, BC = 8, AC = 10. Найти BH.",
           "△ABC прямоугольный (6²+8²=10²). S = ½·6·8 = 24. S = ½·AC·BH → BH = 2·24/10 = 4.8", 3)]),
        ("MET-ADV-GEOM-DOKAZATELSTVO", "Доказательные задачи по геометрии",
         "Доказательство равенства/подобия, параллельности, свойств фигур. Учебник: Атанасян Л.С. 7-9 кл.",
         [("EX-ADV-GEOM-DOK-1", "Доказательство", "Докажите, что медиана треугольника делит его на два равновеликих треугольника.",
           "Медиана AM делит BC на BM = MC. S₁ = ½·BM·h, S₂ = ½·MC·h. BM = MC → S₁ = S₂", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _advanced_functions_ops() -> list[dict]:
    """TOP-MATH-ADVANCED-FUNCTIONS — Функции повышенного уровня (9 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-ADVANCED-FUNCTIONS"
    skill_uid = "SKL-ADVANCED-FUNCTIONS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Функции: задачи повышенного уровня"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-ADV-FUNC-ISSLED", "Исследование функции по графику (ОГЭ ч.2)",
         "Определение свойств функции по формуле: область определения, нули, знакопостоянство, чётность. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-ADV-FUNC-ISS-1", "Исследование функции", "Найти область определения y = √(4-x²).",
           "4 - x² ≥ 0 → x² ≤ 4 → -2 ≤ x ≤ 2. D(f) = [-2, 2]", 2)]),
        ("MET-ADV-FUNC-GRAFICH-METOD", "Графический метод решения уравнений",
         "Заменить уравнение f(x) = g(x) системой y = f(x), y = g(x). Число решений = число пересечений. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-ADV-FUNC-GRAF-1", "Графический метод", "Сколько решений имеет уравнение x² = 2x + 3?",
           "Графики y = x² (парабола) и y = 2x+3 (прямая). Подставим: x²-2x-3 = 0 → x = -1, x = 3. Два решения.", 2)]),
        ("MET-ADV-FUNC-KUSOCHNO", "Кусочно-заданные функции",
         "Функция задаётся разными формулами на разных промежутках. Учебник: Макарычев Ю.Н. 9 кл.",
         [("EX-ADV-FUNC-KUS-1", "Кусочная функция", "f(x) = x², если x < 0; f(x) = 2x, если x ≥ 0. Найти f(-3) и f(4).",
           "f(-3) = (-3)² = 9. f(4) = 2·4 = 8", 1)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 9, "user_class_max": 9}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 9, "user_class_max": 9}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


# ---------------------------------------------------------------------------
# 5. EGE Base topics (grade 11)
# ---------------------------------------------------------------------------

def _numbers_calculations_ops() -> list[dict]:
    """TOP-MATH-NUMBERS-CALCULATIONS — Числа и вычисления (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-NUMBERS-CALCULATIONS"
    skill_uid = "SKL-NUMBERS-CALCULATIONS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Числа и практические вычисления"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-NUM-STEPENI", "Свойства степеней",
         "aᵐ·aⁿ = aᵐ⁺ⁿ, (aᵐ)ⁿ = aᵐⁿ, a⁻ⁿ = 1/aⁿ. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-NUM-STEP-1", "Свойства степеней", "Упростить 2³ · 2⁴ / 2⁵",
           "2³⁺⁴⁻⁵ = 2² = 4", 1)]),
        ("MET-NUM-KORNI", "Свойства корней",
         "√(ab) = √a·√b, ⁿ√(aᵐ) = a^(m/n). Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-NUM-KORN-1", "Свойства корней", "Вычислить √50 · √2",
           "√(50·2) = √100 = 10", 1)]),
        ("MET-NUM-VYCHISL-BEZ-KALK", "Вычисления без калькулятора",
         "Приёмы устного счёта: группировка, разложение на удобные множители. ЕГЭ базовый.",
         [("EX-NUM-VYCH-1", "Устный счёт", "Вычислить 25 × 36",
           "25 × 36 = 25 × 4 × 9 = 100 × 9 = 900", 1)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _derivatives_ops() -> list[dict]:
    """TOP-MATH-DERIVATIVES — Производная и её применение (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-DERIVATIVES"
    skill_uid = "SKL-DERIVATIVES"

    ops.append(create_node(skill_uid, "Skill", {"title": "Производная и её применение"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-DERIV-TABLICA", "Таблица производных",
         "(xⁿ)' = nxⁿ⁻¹, (sin x)' = cos x, (cos x)' = -sin x, (eˣ)' = eˣ, (ln x)' = 1/x. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-DERIV-TABL-1", "Производная", "Найти f'(x), если f(x) = 3x⁴ - 2x² + 5",
           "f'(x) = 12x³ - 4x", 2)]),
        ("MET-DERIV-MONOTONNOST", "Исследование на монотонность",
         "f'(x) > 0 → возрастание, f'(x) < 0 → убывание. Экстремум: f'(x₀) = 0, смена знака. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-DERIV-MON-1", "Промежутки монотонности", "Найти промежутки возрастания f(x) = x³ - 3x.",
           "f'(x) = 3x² - 3 = 3(x-1)(x+1). f'(x) > 0 при x < -1 и x > 1. Возрастает на (-∞, -1) ∪ (1, +∞)", 2)]),
        ("MET-DERIV-NAIBOLSHEE", "Наибольшее и наименьшее значение на отрезке",
         "Найти f'(x) = 0 → критические точки. Сравнить f в критических точках и на концах отрезка. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-DERIV-NAIB-1", "Наибольшее значение", "Найти наибольшее значение f(x) = -x² + 4x на [0, 5].",
           "f'(x) = -2x + 4 = 0 → x = 2. f(0) = 0, f(2) = 4, f(5) = -5. Наибольшее: 4", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _stereometry_ops() -> list[dict]:
    """TOP-MATH-STEREOMETRY — Стереометрия: объёмы и площади (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-STEREOMETRY"
    skill_uid = "SKL-STEREOMETRY"

    ops.append(create_node(skill_uid, "Skill", {"title": "Стереометрия: объёмы и площади"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-STER-PRIZMA", "Объём и площадь поверхности призмы",
         "V = S_осн · h. S_полн = 2S_осн + S_бок. Для прямой призмы S_бок = P_осн · h. Учебник: Атанасян Л.С. 10-11 кл.",
         [("EX-STER-PRIZMA-1", "Объём призмы", "Прямая призма с основанием — прямоугольник 3×4, высота 5. Найти V.",
           "S_осн = 3 × 4 = 12. V = 12 × 5 = 60", 2)]),
        ("MET-STER-PIRAMIDA", "Объём пирамиды",
         "V = ⅓ · S_осн · h. Учебник: Атанасян Л.С. 10-11 кл.",
         [("EX-STER-PIR-1", "Объём пирамиды", "Правильная четырёхугольная пирамида, сторона основания 6, высота 4. Найти V.",
           "S_осн = 6² = 36. V = ⅓ × 36 × 4 = 48", 2)]),
        ("MET-STER-TSILINDER-KONUS", "Цилиндр, конус, шар",
         "V_ц = πr²h, V_к = ⅓πr²h, V_ш = ⁴⁄₃πr³. Учебник: Атанасян Л.С. 10-11 кл.",
         [("EX-STER-SHAR-1", "Объём шара", "Радиус шара 3. Найти объём.",
           "V = 4/3 · π · 27 = 36π ≈ 113.1", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


# ---------------------------------------------------------------------------
# 6. EGE Profile topics (grade 11)
# ---------------------------------------------------------------------------

def _trigonometry_ops() -> list[dict]:
    """TOP-MATH-TRIGONOMETRY — Тригонометрия (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-TRIGONOMETRY"
    skill_uid = "SKL-TRIGONOMETRY"

    ops.append(create_node(skill_uid, "Skill", {"title": "Тригонометрия"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-TRIG-OKRUZHNOST", "Единичная окружность и значения тригонометрических функций",
         "sin, cos, tg, ctg — определение на единичной окружности. Табличные значения для 0°, 30°, 45°, 60°, 90°. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-TRIG-OKR-1", "Значения тригонометрических функций", "Найти sin 150° и cos 150°.",
           "sin 150° = sin(180° - 30°) = sin 30° = 0.5. cos 150° = -cos 30° = -√3/2", 2)]),
        ("MET-TRIG-URAVNENIYA", "Простейшие тригонометрические уравнения",
         "sin x = a → x = (-1)ⁿ arcsin a + πn. cos x = a → x = ±arccos a + 2πn. tg x = a → x = arctg a + πn. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-TRIG-UR-1", "Тригонометрическое уравнение", "Решить sin x = ½.",
           "x = (-1)ⁿ · π/6 + πn, n ∈ ℤ", 2)]),
        ("MET-TRIG-TOZHDESTVA", "Тригонометрические тождества и формулы",
         "sin²x + cos²x = 1. sin 2x = 2 sin x cos x. cos 2x = cos²x - sin²x. Формулы приведения. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-TRIG-TOZH-1", "Тождества", "Упростить sin²x + cos²x + tg²x · cos²x.",
           "sin²x + cos²x + sin²x = 1 + sin²x", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _exp_log_ops() -> list[dict]:
    """TOP-MATH-EXP-LOG — Показательные и логарифмические функции (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-EXP-LOG"
    skill_uid = "SKL-EXP-LOG"

    ops.append(create_node(skill_uid, "Skill", {"title": "Показательные и логарифмические функции"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-EXPLOG-SVOJSTVA-LOG", "Свойства логарифмов",
         "log_a(xy) = log_a(x) + log_a(y). log_a(x/y) = log_a(x) - log_a(y). log_a(xⁿ) = n·log_a(x). Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-EXPLOG-SV-1", "Свойства логарифмов", "Вычислить log₂(8) + log₂(4).",
           "log₂(8) + log₂(4) = log₂(8·4) = log₂(32) = 5", 2)]),
        ("MET-EXPLOG-POKAZAT-NERAV", "Показательные неравенства",
         "aᶠ⁽ˣ⁾ > aᵍ⁽ˣ⁾: при a > 1 → f(x) > g(x); при 0 < a < 1 → f(x) < g(x). Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-EXPLOG-PN-1", "Показательное неравенство", "Решить 2ˣ > 8.",
           "2ˣ > 2³. Основание 2 > 1 → x > 3. Ответ: (3, +∞)", 2)]),
        ("MET-EXPLOG-LOGARIFM-NERAV", "Логарифмические неравенства",
         "log_a(f(x)) > b ⟺ f(x) > aᵇ (a>1) или f(x) < aᵇ (0<a<1). ОДЗ: f(x) > 0. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-EXPLOG-LN-1", "Логарифмическое неравенство", "Решить log₃(x-1) ≤ 2.",
           "ОДЗ: x > 1. Основание 3 > 1 → x - 1 ≤ 9 → x ≤ 10. Ответ: (1, 10]", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _calculus_ops() -> list[dict]:
    """TOP-MATH-CALCULUS — Производная и интеграл, профиль (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-CALCULUS"
    skill_uid = "SKL-CALCULUS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Производная и интеграл (профиль)"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-CALC-SLOZH-PROIZV", "Производная сложной функции",
         "(f(g(x)))' = f'(g(x)) · g'(x). Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-CALC-SLOZH-1", "Сложная производная", "Найти производную y = sin(3x+1).",
           "y' = cos(3x+1) · 3 = 3cos(3x+1)", 3)]),
        ("MET-CALC-PERVOOBRAZNAYA", "Первообразная и таблица интегралов",
         "∫xⁿ dx = xⁿ⁺¹/(n+1) + C. ∫sin x dx = -cos x + C. ∫eˣ dx = eˣ + C. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-CALC-PERV-1", "Первообразная", "Найти ∫(3x² + 2x) dx.",
           "x³ + x² + C", 2)]),
        ("MET-CALC-OPRED-INTEGRAL", "Определённый интеграл и площадь",
         "∫ₐᵇ f(x)dx = F(b) - F(a). Площадь под кривой. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-CALC-OPINT-1", "Определённый интеграл", "Вычислить ∫₀² (x² + 1) dx.",
           "F(x) = x³/3 + x. F(2) - F(0) = 8/3 + 2 - 0 = 14/3 ≈ 4.67", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _advanced_trig_ops() -> list[dict]:
    """TOP-MATH-ADVANCED-TRIG — Тригонометрические уравнения: сложные (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-ADVANCED-TRIG"
    skill_uid = "SKL-ADVANCED-TRIG"

    ops.append(create_node(skill_uid, "Skill", {"title": "Тригонометрические уравнения: сложные случаи"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-ADTRIG-ODNORODNYE", "Однородные тригонометрические уравнения",
         "a·sin²x + b·sin x·cos x + c·cos²x = 0. Делим на cos²x → квадратное относительно tg x. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-ADTRIG-ODN-1", "Однородное уравнение", "Решить sin²x - 3sin x·cos x + 2cos²x = 0.",
           "Делим на cos²x: tg²x - 3tg x + 2 = 0 → (tg x - 1)(tg x - 2) = 0. tg x = 1 → x = π/4 + πn. tg x = 2 → x = arctg 2 + πn", 3)]),
        ("MET-ADTRIG-ZAMENA", "Метод замены переменной в тригонометрических уравнениях",
         "Замена t = sin x, t = cos x, t = tg(x/2) (универсальная подстановка). Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-ADTRIG-ZAM-1", "Замена переменной", "Решить 2cos²x - 5cos x + 2 = 0.",
           "t = cos x. 2t²-5t+2 = 0. t = 2 (не подходит: |cos x| ≤ 1), t = 0.5. cos x = 0.5 → x = ±π/3 + 2πn", 3)]),
        ("MET-ADTRIG-OTBOR", "Отбор корней на промежутке",
         "После нахождения общего решения подставить значения n для попадания в заданный промежуток. Учебник: Алимов Ш.А. 10-11 кл.",
         [("EX-ADTRIG-OTB-1", "Отбор корней", "Отобрать корни sin x = ½ на [0, 2π].",
           "x = (-1)ⁿ·π/6 + πn. При n=0: x = π/6 ∈ [0,2π] ✓. При n=1: x = π - π/6 = 5π/6 ∈ [0,2π] ✓. Ответ: π/6, 5π/6", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _stereometry_advanced_ops() -> list[dict]:
    """TOP-MATH-STEREOMETRY-ADVANCED — Стереометрия: расстояния и углы (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-STEREOMETRY-ADVANCED"
    skill_uid = "SKL-STEREOMETRY-ADVANCED"

    ops.append(create_node(skill_uid, "Skill", {"title": "Стереометрия: расстояния и углы"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-STER-ADV-KOORDINAT", "Координатный метод в пространстве",
         "Ввести систему координат, найти координаты точек, вычислить расстояния и углы через скалярное произведение. Учебник: Атанасян Л.С. 10-11 кл.",
         [("EX-STER-ADV-KOORD-1", "Координатный метод", "Куб ABCDA₁B₁C₁D₁ с ребром 1. Найти расстояние от A до BD₁.",
           "A(0,0,0), B(1,0,0), D₁(0,1,1). BD₁ = (-1,1,1). AB = (1,0,0). Расстояние = |AB × BD₁|/|BD₁| = |(0,−1,1)|/√3 = √2/√3 = √6/3", 3)]),
        ("MET-STER-ADV-SECHENIYA", "Построение сечений многогранников",
         "Метод следов: строить сечение через пересечения плоскости сечения с гранями. Учебник: Атанасян Л.С. 10-11 кл.",
         [("EX-STER-ADV-SECH-1", "Сечение куба", "Построить сечение куба ABCDA₁B₁C₁D₁ плоскостью через середины AB, BC и точку D₁.",
           "M — середина AB, N — середина BC. Сечение: MND₁ — треугольник. MN ∥ AC, MN = AC/2", 3)]),
        ("MET-STER-ADV-UGOL", "Угол между плоскостями и прямой с плоскостью",
         "Угол между прямой и плоскостью: sin φ = |n⃗·a⃗|/(|n⃗|·|a⃗|). Двугранный угол через нормали. Учебник: Атанасян Л.С. 10-11 кл.",
         [("EX-STER-ADV-UG-1", "Угол между прямой и плоскостью", "Прямая проходит через (0,0,0) и (1,1,1). Найти угол с плоскостью Oxy.",
           "Направляющий вектор (1,1,1). Нормаль к Oxy: (0,0,1). sin φ = |1|/√3 = 1/√3 → φ = arcsin(1/√3) ≈ 35.3°", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _financial_advanced_ops() -> list[dict]:
    """TOP-MATH-FINANCIAL-ADVANCED — Финансово-экономические расчёты, профиль (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-FINANCIAL-ADVANCED"
    skill_uid = "SKL-FINANCIAL-ADVANCED"

    ops.append(create_node(skill_uid, "Skill", {"title": "Финансово-экономические расчёты (профиль)"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-FIN-ANNUITET", "Аннуитетный кредит",
         "Ежемесячный платёж A = S · r(1+r)ⁿ / ((1+r)ⁿ - 1), где r — месячная ставка, n — число месяцев. ЕГЭ профиль.",
         [("EX-FIN-ANN-1", "Аннуитетный кредит", "Кредит 1 000 000 руб. на 2 года под 12% годовых (1% в месяц). Найти ежемесячный платёж.",
           "r = 0.01, n = 24. A = 1000000 · 0.01·1.01²⁴/(1.01²⁴-1) = 1000000 · 0.01·1.2697/0.2697 ≈ 47073 руб.", 3)]),
        ("MET-FIN-DIFFERENTSIROV", "Дифференцированный кредит",
         "Основной долг равными частями: d = S/n. Проценты на остаток: Pₖ = (S - (k-1)d) · r. Платёж: Aₖ = d + Pₖ. ЕГЭ профиль.",
         [("EX-FIN-DIFF-1", "Дифференцированный кредит", "Кредит 240000 руб. на 4 месяца под 5% в месяц. Найти 1-й и 2-й платежи.",
           "d = 60000. P₁ = 240000 × 0.05 = 12000. A₁ = 72000. P₂ = 180000 × 0.05 = 9000. A₂ = 69000", 3)]),
        ("MET-FIN-VKLAD-KAPIT", "Вклады с капитализацией",
         "S = S₀(1 + r)ⁿ — сложные проценты. Нахождение срока: n = log(S/S₀)/log(1+r). ЕГЭ профиль.",
         [("EX-FIN-VKLAD-1", "Вклад с капитализацией", "За сколько лет вклад удвоится при ставке 10% годовых с ежегодной капитализацией?",
           "2 = 1.1ⁿ → n = log 2 / log 1.1 = 0.3010/0.0414 ≈ 7.27 → 8 лет", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _advanced_plane_geom_proof_ops() -> list[dict]:
    """TOP-MATH-ADVANCED-PLANE-GEOM-PROOF — Планиметрия: доказательство (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF"
    skill_uid = "SKL-ADVANCED-PLANE-GEOM-PROOF"

    ops.append(create_node(skill_uid, "Skill", {"title": "Планиметрия: доказательство и вычисление"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-GEOMPROOF-VPISANNYE", "Свойства вписанных и описанных окружностей",
         "Вписанный угол = ½ дуги. Касательная перпендикулярна радиусу. Теорема о секущих. Учебник: Атанасян Л.С. 8-9 кл.",
         [("EX-GEOMPROOF-VP-1", "Вписанная окружность", "В четырёхугольник ABCD вписана окружность. AB + CD = BC + AD. Доказать.",
           "AB + CD = BC + AD — свойство описанного четырёхугольника (суммы противоположных сторон равны). Касательные из одной точки равны: AP = AQ, BP = BR, CR = CS, DQ = DS. AB + CD = (AP+BP) + (CS+DS) = (AQ+DQ) + (BR+CR) = AD + BC", 3)]),
        ("MET-GEOMPROOF-DOPPOSTROENIE", "Метод дополнительных построений",
         "Провести высоту, медиану, биссектрису, параллельную прямую для создания подобных/равных треугольников. ЕГЭ профиль.",
         [("EX-GEOMPROOF-DOP-1", "Дополнительное построение", "В △ABC ∠C = 90°, CD — высота на AB. Доказать: AC² = AD · AB.",
           "△ACD ~ △ACB (∠A общий, ∠ACD = ∠ABC = 90° - ∠A). AC/AB = AD/AC → AC² = AD · AB", 3)]),
        ("MET-GEOMPROOF-TRIGON-PLANIMETR", "Тригонометрия в планиметрии",
         "Применение sin, cos, tg к вычислению элементов фигур. Формула площади S = ½ab sin C. ЕГЭ профиль.",
         [("EX-GEOMPROOF-TRIG-1", "Тригонометрия в планиметрии", "В △ABC: a = 8, b = 5, ∠C = 60°. Найти площадь и c.",
           "S = ½·8·5·sin 60° = 20·(√3/2) = 10√3. c² = 64+25-80·0.5 = 49 → c = 7", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _optimization_ops() -> list[dict]:
    """TOP-MATH-OPTIMIZATION — Производная: оптимизация (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-OPTIMIZATION"
    skill_uid = "SKL-OPTIMIZATION"

    ops.append(create_node(skill_uid, "Skill", {"title": "Производная: оптимизация"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-OPT-NAIBOLSHEE-FUNC", "Наибольшее/наименьшее значение функции",
         "1) Найти f'(x) = 0 → критические точки. 2) Сравнить значения на концах и в критических точках. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-OPT-NAIB-1", "Наибольшее значение", "Найти наименьшее значение f(x) = x³ - 3x + 2 на [-2, 2].",
           "f'(x) = 3x²-3 = 0 → x = ±1. f(-2) = -8+6+2 = 0, f(-1) = -1+3+2 = 4, f(1) = 1-3+2 = 0, f(2) = 8-6+2 = 4. Наименьшее: 0", 3)]),
        ("MET-OPT-PRIKLADNAYA", "Прикладные задачи на оптимизацию",
         "Составить функцию одной переменной из условия задачи, найти экстремум. ЕГЭ профиль.",
         [("EX-OPT-PRIKL-1", "Прикладная оптимизация", "Из листа картона 20×30 вырезают квадраты по углам со стороной x и сгибают коробку. При каком x объём максимален?",
           "V(x) = x(20-2x)(30-2x). V'(x) = 12x²-200x+600 = 0. x = (200-√(40000-28800))/24 = (200-√11200)/24 ≈ 3.92 см", 3)]),
        ("MET-OPT-GEOM-ZADACHI", "Геометрические задачи на оптимизацию",
         "Максимальная площадь/объём при фиксированном периметре/площади поверхности. ЕГЭ профиль.",
         [("EX-OPT-GEOM-1", "Геометрическая оптимизация", "Среди прямоугольников с периметром 20 найти прямоугольник наибольшей площади.",
           "2(a+b) = 20 → b = 10-a. S = a(10-a) = -a²+10a. S'= -2a+10 = 0 → a = 5, b = 5. S_max = 25 (квадрат)", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _number_theory_ops() -> list[dict]:
    """TOP-MATH-NUMBER-THEORY — Диофантовы уравнения (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-NUMBER-THEORY"
    skill_uid = "SKL-NUMBER-THEORY"

    ops.append(create_node(skill_uid, "Skill", {"title": "Диофантовы уравнения и целочисленные задачи"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-NT-OSTATKI", "Метод остатков (модульная арифметика)",
         "a ≡ b (mod n) означает n | (a - b). Свойства: если a ≡ b и c ≡ d (mod n), то a+c ≡ b+d и ac ≡ bd. ЕГЭ профиль.",
         [("EX-NT-OST-1", "Метод остатков", "Доказать, что n² + n чётно для любого целого n.",
           "n(n+1) — произведение двух последовательных чисел. Одно из них чётное → произведение чётно", 2)]),
        ("MET-NT-DELIMOST", "Признаки делимости и НОД/НОК",
         "Делимость на 2, 3, 4, 5, 9, 11. Алгоритм Евклида: НОД(a,b) = НОД(b, a mod b). ЕГЭ профиль.",
         [("EX-NT-DELIM-1", "НОД через алгоритм Евклида", "Найти НОД(252, 198).",
           "252 = 1·198 + 54. 198 = 3·54 + 36. 54 = 1·36 + 18. 36 = 2·18 + 0. НОД = 18", 2)]),
        ("MET-NT-DIOFANTOVO", "Решение диофантовых уравнений",
         "Целочисленные уравнения. Метод: разложение, оценка, перебор с модульной арифметикой. ЕГЭ профиль.",
         [("EX-NT-DIOF-1", "Диофантово уравнение", "Найти все натуральные (x, y): xy + 3x + 2y = 25.",
           "xy + 3x + 2y + 6 = 31 → (x+2)(y+3) = 31. 31 — простое. x+2 = 1 (x<0, не подходит) или x+2 = 31 → x = 29, y+3 = 1 → y < 0. Нет натуральных решений.", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _complex_inequalities_ops() -> list[dict]:
    """TOP-MATH-COMPLEX-INEQUALITIES — Иррациональные и трансцендентные неравенства (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-COMPLEX-INEQUALITIES"
    skill_uid = "SKL-COMPLEX-INEQUALITIES"

    ops.append(create_node(skill_uid, "Skill", {"title": "Иррациональные и трансцендентные неравенства"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-CINEQ-IRRATSION", "Иррациональные неравенства",
         "√f(x) > g(x): если g(x) < 0 → f(x) ≥ 0; если g(x) ≥ 0 → f(x) > g²(x). ОДЗ: f(x) ≥ 0. Учебник: Мордкович А.Г. 10-11 кл.",
         [("EX-CINEQ-IRR-1", "Иррациональное неравенство", "Решить √(x-1) ≤ x - 3.",
           "ОДЗ: x ≥ 1, x ≥ 3. При x ≥ 3: x-1 ≤ (x-3)² → x-1 ≤ x²-6x+9 → x²-7x+10 ≥ 0 → (x-2)(x-5) ≥ 0. С учётом x ≥ 3: x ≥ 5. Ответ: [5, +∞)", 3)]),
        ("MET-CINEQ-METOD-INTERVALOV", "Обобщённый метод интервалов",
         "Для неравенства вида f(x)/g(x) > 0: найти нули числителя и знаменателя, отметить на оси, определить знак. Учебник: Мордкович А.Г. 10-11 кл.",
         [("EX-CINEQ-MINT-1", "Метод интервалов", "Решить (x²-4)/(x-3) ≥ 0.",
           "Нули: x = -2, 2, 3 (3 — выколота). Знаки: (-∞,-2]: -, [-2,2]: +, [2,3): -, (3,+∞): +. Ответ: [-2, 2] ∪ (3, +∞)", 3)]),
        ("MET-CINEQ-LOGARIFM-NERAV", "Логарифмические неравенства (сложные)",
         "log_a(f(x)) > log_a(g(x)): при a > 1 → f(x) > g(x) > 0; при 0 < a < 1 → 0 < f(x) < g(x). Учебник: Мордкович А.Г. 10-11 кл.",
         [("EX-CINEQ-LOGN-1", "Сложное логарифмическое неравенство", "Решить log₀.₅(x+2) > log₀.₅(3x).",
           "ОДЗ: x > 0, x > -2 → x > 0. Основание 0.5 < 1 → x+2 < 3x → 2 < 2x → x > 1. Ответ: (1, +∞)", 3)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


def _combinatorics_ops() -> list[dict]:
    """TOP-MATH-COMBINATORICS — Комбинаторика и вероятность, профиль (11 кл)."""
    ops: list[dict] = []
    topic_uid = "TOP-MATH-COMBINATORICS"
    skill_uid = "SKL-COMBINATORICS"

    ops.append(create_node(skill_uid, "Skill", {"title": "Комбинаторика и вероятность (профиль)"}))
    ops.append(create_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    methods = [
        ("MET-COMB-PERESTANOVKI", "Перестановки и размещения",
         "P(n) = n!. A(n,k) = n!/(n-k)!. Правило произведения и суммы. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-COMB-PER-1", "Размещения", "Сколькими способами можно выбрать старосту и его заместителя из 30 учеников?",
           "A(30,2) = 30·29 = 870", 2)]),
        ("MET-COMB-BERNOULLI-PROF", "Формула Бернулли (профильный уровень)",
         "P(k) = C(n,k)·pᵏ·qⁿ⁻ᵏ. Применение к задачам ЕГЭ профильного уровня. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-COMB-BERN-1", "Формула Бернулли", "Вероятность попадания стрелка 0.7. Какова вероятность ровно 4 попаданий из 5 выстрелов?",
           "P(4) = C(5,4) · 0.7⁴ · 0.3¹ = 5 · 0.2401 · 0.3 = 0.36015", 3)]),
        ("MET-COMB-GEOM-VEROYATNOST", "Геометрическая вероятность",
         "P = S_благоприятной_области / S_всей_области. Учебник: Колмогоров А.Н. 10-11 кл.",
         [("EX-COMB-GEOM-1", "Геометрическая вероятность", "Точка случайно выбрана в квадрате 10×10. Какова вероятность, что она попадёт в вписанный круг?",
           "R = 5 (радиус вписанного круга). P = πR²/S_кв = π·25/100 = π/4 ≈ 0.785", 2)]),
    ]
    for m_uid, m_title, m_desc, examples in methods:
        ops.append(create_node(m_uid, "Method", {"title": m_title, "description": m_desc, "user_class_min": 11, "user_class_max": 11}))
        ops.append(create_rel(skill_uid, m_uid, "HAS_METHOD"))
        for ex_uid, ex_title, ex_stmt, ex_sol, diff in examples:
            ops.append(create_node(ex_uid, "Example", {"title": ex_title, "statement": ex_stmt, "solution": ex_sol, "difficulty_level": diff, "user_class_min": 11, "user_class_max": 11}))
            ops.append(create_rel(m_uid, ex_uid, "HAS_EXAMPLE"))

    return ops


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _make_proposal(ops_fn) -> dict:
    """Reset op counter and build a single proposal from an ops function."""
    global _OP_COUNTER
    _OP_COUNTER = 0
    ops = ops_fn()
    return {"base_graph_version": 0, "operations": ops}


def build_proposals() -> list[dict]:
    """Return list of proposal payloads (each is a dict with base_graph_version + operations)."""
    fns = [
        # Original proposals
        _probability_ops,
        _user_topics_ops,
        # Shared OGE+EGE (9-11)
        _equations_systems_ops,
        _plane_geometry_ops,
        _functions_graphs_ops,
        _applied_math_ops,
        # OGE-specific (9)
        _algebra_transforms_ops,
        _inequalities_ops,
        _progressions_ops,
        _advanced_algebra_ops,
        _advanced_plane_geom_ops,
        _advanced_functions_ops,
        # EGE Base (11)
        _numbers_calculations_ops,
        _derivatives_ops,
        _stereometry_ops,
        # EGE Profile (11)
        _trigonometry_ops,
        _exp_log_ops,
        _calculus_ops,
        _advanced_trig_ops,
        _stereometry_advanced_ops,
        _financial_advanced_ops,
        _advanced_plane_geom_proof_ops,
        _optimization_ops,
        _number_theory_ops,
        _complex_inequalities_ops,
        _combinatorics_ops,
    ]
    return [_make_proposal(fn) for fn in fns]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print JSON proposals without submitting")
    parser.add_argument("--kb-url", default="http://localhost:8000", help="KnowledgeBaseAI base URL")
    parser.add_argument("--tenant-id", default="default", help="Tenant ID header value")
    args = parser.parse_args()

    proposals = build_proposals()

    if args.dry_run:
        for i, p in enumerate(proposals, 1):
            print(f"\n=== Proposal {i} ({len(p['operations'])} operations) ===")
            print(json.dumps(p, ensure_ascii=False, indent=2))
        print(f"\nTotal: {sum(len(p['operations']) for p in proposals)} operations across {len(proposals)} proposals")
        return

    # Submit proposals via HTTP
    try:
        import httpx
    except ImportError:
        print("httpx not installed. Run: pip install httpx", file=sys.stderr)
        sys.exit(1)

    client = httpx.Client(base_url=args.kb_url, timeout=30)
    headers = {"X-Tenant-ID": args.tenant_id}

    for i, payload in enumerate(proposals, 1):
        print(f"\n--- Submitting proposal {i} ({len(payload['operations'])} ops)...")
        resp = client.post("/v1/proposals", json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"  ERROR creating proposal: {resp.status_code} {resp.text}", file=sys.stderr)
            continue

        data = resp.json()
        items = data.get("items", [])
        if not items:
            print(f"  ERROR: no items in response: {data}", file=sys.stderr)
            continue

        proposal_id = items[0].get("proposal_id")
        print(f"  Created proposal: {proposal_id}")

        # Commit
        commit_resp = client.post(f"/v1/proposals/{proposal_id}/commit", headers=headers)
        if commit_resp.status_code == 200:
            commit_data = commit_resp.json()
            commit_items = commit_data.get("items", [{}])
            ok = commit_items[0].get("ok", False) if commit_items else False
            if ok:
                print(f"  Committed successfully! graph_version={commit_items[0].get('graph_version')}")
            else:
                print(f"  Commit failed: {commit_items}", file=sys.stderr)
        else:
            print(f"  ERROR committing: {commit_resp.status_code} {commit_resp.text}", file=sys.stderr)

    client.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
