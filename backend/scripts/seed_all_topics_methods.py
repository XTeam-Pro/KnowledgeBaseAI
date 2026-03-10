#!/usr/bin/env python3
"""Seed grade-specific Method + Example nodes for ALL remaining topics.

Creates proposals via the KB proposal API. Each topic gets 3 methods per
grade band with 1-2 examples each. Content is based on official Russian
mathematics textbooks:
  - 2-4 kl: Моро М.И.
  - 5-6 kl: Виленкин Н.Я., Мерзляк А.Г.
  - 7-9 kl: Макарычев Ю.Н., Атанасян Л.С., Мерзляк А.Г.
  - 10-11 kl: Алимов Ш.А., Колмогоров А.Н., Мордкович А.Г.

Usage:
    python scripts/seed_all_topics_methods.py [--dry-run] [--section SECTION]
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


def _node(uid: str, node_type: str, props: dict[str, Any]) -> dict:
    return {
        "op_id": _next_op_id(),
        "op_type": "CREATE_NODE",
        "target_id": uid,
        "properties_delta": {"type": node_type, **props},
        "evidence": {"source_chunk_id": "seed_all_topics", "quote": props.get("title", "")},
    }


def _rel(from_uid: str, to_uid: str, rel_type: str) -> dict:
    return {
        "op_id": _next_op_id(),
        "op_type": "CREATE_REL",
        "properties_delta": {"type": rel_type, "from_uid": from_uid, "to_uid": to_uid},
        "evidence": {"source_chunk_id": "seed_all_topics", "quote": f"{from_uid}->{to_uid}"},
    }


def _build_ops_from_topic_def(topic_uid: str, skill_uid: str, skill_title: str,
                               bands: list[dict]) -> list[dict]:
    """Generic builder: topic_uid already exists, create Skill + Methods + Examples.

    bands = [
        {
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {
                    "uid": "MET-...", "title": "...", "description": "...",
                    "examples": [
                        {"uid": "EX-...", "title": "...", "statement": "...",
                         "solution": "...", "difficulty_level": 1},
                    ]
                },
                ...
            ]
        },
        ...
    ]
    """
    ops: list[dict] = []
    ops.append(_node(skill_uid, "Skill", {"title": skill_title}))
    ops.append(_rel(topic_uid, skill_uid, "REQUIRES_SKILL"))

    for band in bands:
        uc_min, uc_max = band["uc_min"], band["uc_max"]
        for m in band["methods"]:
            ops.append(_node(m["uid"], "Method", {
                "title": m["title"],
                "description": m["description"],
                "user_class_min": uc_min,
                "user_class_max": uc_max,
            }))
            ops.append(_rel(skill_uid, m["uid"], "HAS_METHOD"))
            for ex in m.get("examples", []):
                ops.append(_node(ex["uid"], "Example", {
                    "title": ex["title"],
                    "statement": ex["statement"],
                    "solution": ex["solution"],
                    "difficulty_level": ex.get("difficulty_level", 1),
                    "user_class_min": uc_min,
                    "user_class_max": uc_max,
                }))
                ops.append(_rel(m["uid"], ex["uid"], "HAS_EXAMPLE"))
    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Арифметика  (6 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _arithmetic_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Натуральные числа (5-6 кл, Виленкин)
    ops += _build_ops_from_topic_def(
        "TOP-NATURALNYE-CHISLA-b27027", "SKL-NATURALNYE-CHISLA-SEED", "Натуральные числа",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-NAT-SRAVNENIE", "title": "Сравнение натуральных чисел",
                 "description": "Сравнение по разрядам слева направо. Число с большим количеством разрядов больше. Виленкин Н.Я. 5 кл., §1.",
                 "examples": [
                     {"uid": "EX-NAT-SRAV-1", "title": "Сравнение многозначных чисел",
                      "statement": "Сравните 3 578 и 3 587.",
                      "solution": "Тысячи равны (3=3), сотни равны (5=5), десятки: 7 < 8, значит 3 578 < 3 587.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-NAT-OKRUGLENIE", "title": "Округление натуральных чисел",
                 "description": "Если цифра после разряда округления ≥ 5, увеличиваем разряд на 1, остальные заменяем нулями. Виленкин Н.Я. 5 кл., §1.",
                 "examples": [
                     {"uid": "EX-NAT-OKRUGL-1", "title": "Округление до тысяч",
                      "statement": "Округлите 12 456 до тысяч.",
                      "solution": "Смотрим на сотни: 4 < 5, значит 12 456 ≈ 12 000.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-NAT-KOORD-LUCH", "title": "Координатный луч",
                 "description": "Отмечаем натуральные числа на луче с единичным отрезком. Чем правее точка, тем больше число. Виленкин Н.Я. 5 кл., §1.",
                 "examples": [
                     {"uid": "EX-NAT-KOORD-1", "title": "Точки на координатном луче",
                      "statement": "Отметьте на координатном луче точки A(3), B(7), C(5). Какая из них расположена правее?",
                      "solution": "B(7) правее всех, так как 7 > 5 > 3.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 2. Операции и свойства (5-6 кл, Виленкин)
    ops += _build_ops_from_topic_def(
        "TOP-OPERATSII-I-SVOJSTVA-b8ac93", "SKL-OPERATSII-SVOJSTVA-SEED", "Арифметические операции и свойства",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-OP-PEREMEST", "title": "Переместительное и сочетательное свойства",
                 "description": "a + b = b + a, a · b = b · a (переместительное). (a + b) + c = a + (b + c) (сочетательное). Позволяют группировать слагаемые/множители для удобства вычислений. Виленкин Н.Я. 5 кл., §2.",
                 "examples": [
                     {"uid": "EX-OP-PEREM-1", "title": "Удобная группировка",
                      "statement": "Вычислите удобным способом: 25 · 37 · 4.",
                      "solution": "25 · 4 · 37 = 100 · 37 = 3 700.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-OP-RASPRED", "title": "Распределительное свойство умножения",
                 "description": "a · (b + c) = a · b + a · c. Используется для упрощения вычислений и раскрытия скобок. Виленкин Н.Я. 5 кл., §2.",
                 "examples": [
                     {"uid": "EX-OP-RASPR-1", "title": "Раскрытие скобок",
                      "statement": "Вычислите: 98 · 15.",
                      "solution": "98 · 15 = (100 − 2) · 15 = 1500 − 30 = 1 470.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-OP-STOLBIK", "title": "Сложение и умножение столбиком",
                 "description": "Запись чисел друг под другом по разрядам. Сложение/умножение поразрядно с переносом. Виленкин Н.Я. 5 кл., §2.",
                 "examples": [
                     {"uid": "EX-OP-STOLB-1", "title": "Умножение столбиком",
                      "statement": "Вычислите столбиком: 347 × 26.",
                      "solution": "347 × 6 = 2 082; 347 × 20 = 6 940; 2 082 + 6 940 = 9 022.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 3. Порядок действий (5-6 кл, Виленкин)
    ops += _build_ops_from_topic_def(
        "TOP-PORYADOK-DEJSTVIJ-006", "SKL-PORYADOK-DEJSTVIJ-SEED", "Порядок действий",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-POR-SKOBKI", "title": "Порядок: скобки → степени → умножение/деление → сложение/вычитание",
                 "description": "1) Скобки, 2) Степени, 3) Умножение и деление (слева направо), 4) Сложение и вычитание (слева направо). Виленкин Н.Я. 5 кл., §2.",
                 "examples": [
                     {"uid": "EX-POR-1", "title": "Вычисление по порядку",
                      "statement": "Найдите значение: 36 − 2 · (18 − 13) + 4.",
                      "solution": "1) 18 − 13 = 5; 2) 2 · 5 = 10; 3) 36 − 10 + 4 = 30.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-POR-VLOZH-SKOBKI", "title": "Вложенные скобки",
                 "description": "При наличии вложенных скобок вычисление начинается с самых внутренних. Виленкин Н.Я. 5 кл., §2.",
                 "examples": [
                     {"uid": "EX-POR-VLOZH-1", "title": "Вложенные скобки",
                      "statement": "Вычислите: 100 − (40 + 3 · (12 − 7)).",
                      "solution": "1) 12 − 7 = 5; 2) 3 · 5 = 15; 3) 40 + 15 = 55; 4) 100 − 55 = 45.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-POR-DROBNYJ", "title": "Порядок действий в дробных выражениях",
                 "description": "Числитель и знаменатель дроби вычисляются отдельно, затем деление. Черта дроби равносильна скобкам. Виленкин Н.Я. 5 кл., §5.",
                 "examples": [
                     {"uid": "EX-POR-DROB-1", "title": "Дробное выражение",
                      "statement": "Вычислите: (24 + 6) / (15 − 10).",
                      "solution": "Числитель: 24 + 6 = 30. Знаменатель: 15 − 10 = 5. Результат: 30 / 5 = 6.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 4. Делимость (5-6 кл, Виленкин)
    ops += _build_ops_from_topic_def(
        "TOP-DELIMOST-7143f5", "SKL-DELIMOST-SEED", "Делимость",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-DEL-PRIZNAKI", "title": "Признаки делимости на 2, 3, 5, 9, 10",
                 "description": "На 2: последняя цифра чётная. На 3: сумма цифр делится на 3. На 5: последняя 0 или 5. На 9: сумма цифр делится на 9. На 10: последняя 0. Виленкин Н.Я. 6 кл., §1.",
                 "examples": [
                     {"uid": "EX-DEL-PRIZN-1", "title": "Признаки делимости",
                      "statement": "Определите, делится ли 2 346 на 3 и на 9.",
                      "solution": "Сумма цифр: 2+3+4+6 = 15. 15 ÷ 3 = 5 (делится на 3). 15 ÷ 9 = 1 ост. 6 (не делится на 9).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-DEL-RAZLOZHENIE", "title": "Разложение на простые множители",
                 "description": "Последовательно делим число на наименьший простой делитель. Виленкин Н.Я. 6 кл., §1.",
                 "examples": [
                     {"uid": "EX-DEL-RAZL-1", "title": "Разложение числа",
                      "statement": "Разложите 180 на простые множители.",
                      "solution": "180 = 2 · 90 = 2 · 2 · 45 = 2 · 2 · 3 · 15 = 2 · 2 · 3 · 3 · 5 = 2² · 3² · 5.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-DEL-DELENIYE-S-OST", "title": "Деление с остатком",
                 "description": "a = b · q + r, где 0 ≤ r < b. q — неполное частное, r — остаток. Виленкин Н.Я. 5 кл., §1.",
                 "examples": [
                     {"uid": "EX-DEL-OST-1", "title": "Деление с остатком",
                      "statement": "Найдите частное и остаток при делении 157 на 12.",
                      "solution": "157 = 12 · 13 + 1. Частное: 13, остаток: 1.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 5. Целые числа (5-7 кл, Виленкин 6, Макарычев 7)
    ops += _build_ops_from_topic_def(
        "TOP-TSELYE-CHISLA-23a63f", "SKL-TSELYE-CHISLA-SEED", "Целые числа",
        [
            {
                "uc_min": 5, "uc_max": 6,
                "methods": [
                    {"uid": "MET-TSEL-MODUL", "title": "Модуль числа",
                     "description": "Модуль числа a — расстояние от начала координат до точки a на координатной прямой. |a| ≥ 0. |a| = a при a ≥ 0; |a| = −a при a < 0. Виленкин Н.Я. 6 кл., §5.",
                     "examples": [
                         {"uid": "EX-TSEL-MOD-1", "title": "Нахождение модуля",
                          "statement": "Найдите |−7|, |4|, |0|.",
                          "solution": "|−7| = 7, |4| = 4, |0| = 0.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TSEL-SLOZH-OTRITS", "title": "Сложение и вычитание отрицательных чисел",
                     "description": "a + (−b) = a − b. (−a) + (−b) = −(a + b). При сложении чисел с разными знаками: из большего модуля вычитаем меньший, ставим знак числа с большим модулем. Виленкин Н.Я. 6 кл., §6.",
                     "examples": [
                         {"uid": "EX-TSEL-SLOZH-1", "title": "Сложение отрицательных",
                          "statement": "Вычислите: (−8) + 5 + (−3).",
                          "solution": "(−8) + 5 = −3; (−3) + (−3) = −6.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TSEL-UMNOZH-OTRITS", "title": "Умножение и деление целых чисел",
                     "description": "Минус на минус — плюс: (−a)(−b) = ab. Плюс на минус — минус: a(−b) = −ab. Аналогично для деления. Виленкин Н.Я. 6 кл., §7.",
                     "examples": [
                         {"uid": "EX-TSEL-UMNOZH-1", "title": "Умножение отрицательных",
                          "statement": "Вычислите: (−6) · (−4) · (−1).",
                          "solution": "(−6)(−4) = 24; 24 · (−1) = −24.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 7, "uc_max": 7,
                "methods": [
                    {"uid": "MET-TSEL-SRAV-KOORD", "title": "Сравнение целых чисел на координатной прямой",
                     "description": "На координатной прямой меньшее число стоит левее. Для отрицательных чисел: чем больше модуль, тем меньше число. Макарычев Ю.Н. 7 кл., §1.",
                     "examples": [
                         {"uid": "EX-TSEL-SRAV-7-1", "title": "Сравнение на прямой",
                          "statement": "Расположите в порядке возрастания: −5, 3, −1, 0, −8.",
                          "solution": "−8 < −5 < −1 < 0 < 3.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TSEL-STEPEN-7", "title": "Степень целого числа",
                     "description": "aⁿ = a · a · ... · a (n раз). (−a)²ⁿ > 0, (−a)²ⁿ⁺¹ < 0. Макарычев Ю.Н. 7 кл., §4.",
                     "examples": [
                         {"uid": "EX-TSEL-STEP-7-1", "title": "Степень отрицательного числа",
                          "statement": "Вычислите: (−2)³ и (−2)⁴.",
                          "solution": "(−2)³ = −8; (−2)⁴ = 16.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TSEL-RAZLOZH-7", "title": "Разложение на множители с целыми числами",
                     "description": "Вынесение общего множителя: ab + ac = a(b + c). Группировка: ax + ay + bx + by = a(x+y) + b(x+y) = (a+b)(x+y). Макарычев Ю.Н. 7 кл., §7.",
                     "examples": [
                         {"uid": "EX-TSEL-RAZL-7-1", "title": "Вынесение общего множителя",
                          "statement": "Разложите на множители: 6x² − 15x.",
                          "solution": "6x² − 15x = 3x(2x − 5).", "difficulty_level": 1},
                     ]},
                ],
            },
        ],
    )

    # 6. Рациональные числа (6-7 кл)
    ops += _build_ops_from_topic_def(
        "TOP-RATSIONALNYE-CHISLA-dd476c", "SKL-RATSIONALNYE-CHISLA-SEED", "Рациональные числа",
        [
            {
                "uc_min": 6, "uc_max": 6,
                "methods": [
                    {"uid": "MET-RATS-OBYKN-DROBI", "title": "Действия с обыкновенными дробями",
                     "description": "Сложение: a/b + c/d = (ad + bc)/bd. Умножение: a/b · c/d = ac/bd. Деление: a/b ÷ c/d = a/b · d/c. Виленкин Н.Я. 6 кл., §2.",
                     "examples": [
                         {"uid": "EX-RATS-OBYKN-1", "title": "Сложение дробей",
                          "statement": "Вычислите: 2/3 + 3/4.",
                          "solution": "НОЗ = 12. 2/3 = 8/12, 3/4 = 9/12. 8/12 + 9/12 = 17/12 = 1 5/12.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-RATS-DESYAT-DROBI", "title": "Действия с десятичными дробями",
                     "description": "Сложение/вычитание: записать столбиком, выровняв запятые. Умножение: перемножить как целые, отделить запятой сумму десятичных знаков. Виленкин Н.Я. 6 кл., §4.",
                     "examples": [
                         {"uid": "EX-RATS-DES-1", "title": "Умножение десятичных",
                          "statement": "Вычислите: 3.14 × 2.5.",
                          "solution": "314 × 25 = 7 850. В 3.14 два знака, в 2.5 один → три знака: 7.850 = 7.85.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-RATS-PEREVOD", "title": "Перевод между обыкновенной и десятичной дробью",
                     "description": "Обыкн. → десят.: делим числитель на знаменатель. Десят. → обыкн.: записываем дробь с знаменателем 10/100/1000 и сокращаем. Виленкин Н.Я. 6 кл., §4.",
                     "examples": [
                         {"uid": "EX-RATS-PEREV-1", "title": "Перевод дробей",
                          "statement": "Переведите 3/8 в десятичную дробь.",
                          "solution": "3 ÷ 8 = 0.375.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 7, "uc_max": 7,
                "methods": [
                    {"uid": "MET-RATS-URAVNEN-7", "title": "Рациональные числа в уравнениях",
                     "description": "Решение уравнений с дробными коэффициентами: домножаем обе части на НОЗ знаменателей. Макарычев Ю.Н. 7 кл., §3.",
                     "examples": [
                         {"uid": "EX-RATS-URAVN-7-1", "title": "Уравнение с дробями",
                          "statement": "Решите: x/3 + x/4 = 7.",
                          "solution": "НОЗ = 12. 4x + 3x = 84. 7x = 84. x = 12.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-RATS-KOORD-PRYAM-7", "title": "Рациональные числа на координатной прямой",
                     "description": "Любое рациональное число можно представить как точку на координатной прямой. Между любыми двумя есть бесконечно много других. Макарычев Ю.Н. 7 кл., §1.",
                     "examples": [
                         {"uid": "EX-RATS-KOORD-7-1", "title": "Расположение на прямой",
                          "statement": "Какое рациональное число расположено точно посередине между 1/3 и 1/2?",
                          "solution": "(1/3 + 1/2) / 2 = (2/6 + 3/6) / 2 = (5/6) / 2 = 5/12.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-RATS-PERIOD-7", "title": "Периодические десятичные дроби",
                     "description": "Рациональное число в виде десятичной дроби — конечная или бесконечная периодическая. 1/3 = 0.333... = 0.(3). Перевод: составляем уравнение. Макарычев Ю.Н. 7 кл., §1.",
                     "examples": [
                         {"uid": "EX-RATS-PERIOD-7-1", "title": "Периодическая дробь в обыкновенную",
                          "statement": "Переведите 0.(27) в обыкновенную дробь.",
                          "solution": "x = 0.272727... 100x = 27.2727... 100x − x = 27. 99x = 27. x = 27/99 = 3/11.", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Числа и структуры  (6 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _numbers_structures_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Единицы измерения (5-6 кл)
    ops += _build_ops_from_topic_def(
        "TOP-EDINITSY-IZMERENIYA-002", "SKL-EDINITSY-IZMER-SEED", "Единицы измерения",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-EDIZ-DLINA", "title": "Перевод единиц длины",
                 "description": "1 км = 1000 м, 1 м = 100 см = 10 дм, 1 см = 10 мм. Для перевода умножаем/делим на 10/100/1000. Виленкин Н.Я. 5 кл.",
                 "examples": [
                     {"uid": "EX-EDIZ-DL-1", "title": "Перевод метров в сантиметры",
                      "statement": "Выразите 3 м 45 см в сантиметрах.",
                      "solution": "3 м = 300 см. 300 + 45 = 345 см.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-EDIZ-PLOSHCHAD", "title": "Перевод единиц площади",
                 "description": "1 м² = 10 000 см², 1 км² = 1 000 000 м², 1 га = 10 000 м², 1 а (сотка) = 100 м². Виленкин Н.Я. 5 кл.",
                 "examples": [
                     {"uid": "EX-EDIZ-PL-1", "title": "Гектары в квадратные метры",
                      "statement": "Участок площадью 2.5 га. Сколько это квадратных метров?",
                      "solution": "2.5 · 10 000 = 25 000 м².", "difficulty_level": 1},
                 ]},
                {"uid": "MET-EDIZ-VREMYA", "title": "Перевод единиц времени",
                 "description": "1 ч = 60 мин, 1 мин = 60 с, 1 сутки = 24 ч. Перевод: умножаем на соответствующий коэффициент. Виленкин Н.Я. 5 кл.",
                 "examples": [
                     {"uid": "EX-EDIZ-VR-1", "title": "Часы в минуты",
                      "statement": "Выразите 2 ч 35 мин в минутах.",
                      "solution": "2 · 60 + 35 = 120 + 35 = 155 мин.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 2. Текстовые задачи (5-9 кл) — multi-band
    ops += _build_ops_from_topic_def(
        "TOP-TEKSTOVYE-ZADACHI-004", "SKL-TEKSTOVYE-ZADACHI-SEED", "Текстовые задачи",
        [
            {
                "uc_min": 5, "uc_max": 6,
                "methods": [
                    {"uid": "MET-TEKST-SKOROST-56", "title": "Задачи на движение",
                     "description": "S = v · t. При встречном движении: v_сбл = v₁ + v₂. При движении вдогонку: v_сбл = v₁ − v₂. Виленкин Н.Я. 5 кл., §3.",
                     "examples": [
                         {"uid": "EX-TEKST-SKOR-56-1", "title": "Встречное движение",
                          "statement": "Два поезда вышли навстречу. Скорости 60 км/ч и 80 км/ч. Расстояние 420 км. Через сколько встретятся?",
                          "solution": "v_сбл = 60 + 80 = 140 км/ч. t = 420 / 140 = 3 ч.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TEKST-RABOTA-56", "title": "Задачи на совместную работу",
                     "description": "Если один делает работу за a ч, другой за b ч, то вместе: 1/a + 1/b часть работы за 1 час. Время вместе: ab/(a+b). Виленкин Н.Я. 5 кл., §5.",
                     "examples": [
                         {"uid": "EX-TEKST-RAB-56-1", "title": "Совместная работа",
                          "statement": "Один маляр красит забор за 6 ч, второй — за 12 ч. За сколько покрасят вместе?",
                          "solution": "1/6 + 1/12 = 2/12 + 1/12 = 3/12 = 1/4 часть за час. Время: 4 ч.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TEKST-PROPOR-56", "title": "Задачи на пропорции",
                     "description": "Прямая пропорциональность: a₁/b₁ = a₂/b₂. Обратная: a₁ · b₁ = a₂ · b₂. Виленкин Н.Я. 6 кл., §4.",
                     "examples": [
                         {"uid": "EX-TEKST-PROP-56-1", "title": "Пропорция",
                          "statement": "Из 5 кг яблок получается 3.5 л сока. Сколько сока из 8 кг?",
                          "solution": "5/3.5 = 8/x → x = 8 · 3.5 / 5 = 5.6 л.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 7, "uc_max": 9,
                "methods": [
                    {"uid": "MET-TEKST-URAVNEN-79", "title": "Решение текстовых задач через уравнение",
                     "description": "Обозначаем неизвестное за x, составляем уравнение по условию, решаем. Макарычев Ю.Н. 7-9 кл.",
                     "examples": [
                         {"uid": "EX-TEKST-URAVN-79-1", "title": "Задача на возраст",
                          "statement": "Отцу 42 года, сыну 12. Через сколько лет отец будет вдвое старше сына?",
                          "solution": "42 + x = 2(12 + x). 42 + x = 24 + 2x. 18 = x. Через 18 лет.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-TEKST-PROCENTY-79", "title": "Задачи на проценты (сложные)",
                     "description": "Задачи на сплавы, смеси, концентрации. Масса вещества = концентрация × масса раствора. Макарычев Ю.Н. 8 кл.",
                     "examples": [
                         {"uid": "EX-TEKST-PROC-79-1", "title": "Задача на смеси",
                          "statement": "Смешали 200 г 10%-ного и 300 г 20%-ного раствора соли. Найдите концентрацию.",
                          "solution": "Соль: 200·0.1 + 300·0.2 = 20 + 60 = 80 г. Масса: 500 г. Концентрация: 80/500 = 16%.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-TEKST-SISTEMA-79", "title": "Решение текстовых задач через систему уравнений",
                     "description": "Вводим 2 переменных, составляем 2 уравнения по условиям задачи. Макарычев Ю.Н. 9 кл.",
                     "examples": [
                         {"uid": "EX-TEKST-SIST-79-1", "title": "Задача на движение по реке",
                          "statement": "Катер прошёл 48 км по течению за 2 ч и 48 км против за 3 ч. Найдите скорость катера и течения.",
                          "solution": "v + u = 48/2 = 24, v − u = 48/3 = 16. Сложим: 2v = 40, v = 20 км/ч. u = 4 км/ч.", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 3. НОД и НОК (5-6 кл)
    ops += _build_ops_from_topic_def(
        "TOP-NOD-I-NOK-b29ab2", "SKL-NOD-NOK-SEED", "НОД и НОК",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-NOD-RAZLOZH", "title": "НОД через разложение на множители",
                 "description": "Раскладываем оба числа на простые множители. НОД = произведение общих множителей в наименьших степенях. Виленкин Н.Я. 6 кл., §1.",
                 "examples": [
                     {"uid": "EX-NOD-RAZL-1", "title": "НОД двух чисел",
                      "statement": "Найдите НОД(36, 48).",
                      "solution": "36 = 2² · 3². 48 = 2⁴ · 3. НОД = 2² · 3 = 12.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-NOK-RAZLOZH", "title": "НОК через разложение на множители",
                 "description": "НОК = произведение всех множителей в наибольших степенях. НОК(a,b) = a·b / НОД(a,b). Виленкин Н.Я. 6 кл., §1.",
                 "examples": [
                     {"uid": "EX-NOK-RAZL-1", "title": "НОК двух чисел",
                      "statement": "Найдите НОК(12, 18).",
                      "solution": "12 = 2² · 3. 18 = 2 · 3². НОК = 2² · 3² = 36.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-NOK-PRIMENENIE", "title": "Применение НОК для сложения дробей",
                 "description": "Чтобы сложить дроби с разными знаменателями, находим НОК знаменателей (наименьший общий знаменатель). Виленкин Н.Я. 6 кл., §2.",
                 "examples": [
                     {"uid": "EX-NOK-PRIM-1", "title": "Сложение с НОК",
                      "statement": "Вычислите 5/12 + 7/18.",
                      "solution": "НОК(12,18) = 36. 5/12 = 15/36, 7/18 = 14/36. 15/36 + 14/36 = 29/36.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 4. Простые числа (5-6 кл)
    ops += _build_ops_from_topic_def(
        "TOP-PROSTYE-CHISLA-976ead", "SKL-PROSTYE-CHISLA-SEED", "Простые числа",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-PROST-RESHETO", "title": "Решето Эратосфена",
                 "description": "Выписываем числа от 2 до N. Вычёркиваем составные: сначала все кратные 2 (кроме 2), затем кратные 3, 5, 7, ... Оставшиеся — простые. Виленкин Н.Я. 6 кл., §1.",
                 "examples": [
                     {"uid": "EX-PROST-RESH-1", "title": "Простые до 30",
                      "statement": "Найдите все простые числа от 1 до 30.",
                      "solution": "2, 3, 5, 7, 11, 13, 17, 19, 23, 29 — всего 10 простых чисел.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PROST-PROVERKA", "title": "Проверка числа на простоту",
                 "description": "Делим число n на все простые от 2 до √n. Если ни одно не делит — число простое. Виленкин Н.Я. 6 кл., §1.",
                 "examples": [
                     {"uid": "EX-PROST-PROV-1", "title": "Проверка числа 97",
                      "statement": "Является ли число 97 простым?",
                      "solution": "√97 ≈ 9.8. Проверяем деление на 2, 3, 5, 7. 97/2, 97/3, 97/5, 97/7 — ни одно не даёт целого. 97 — простое.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PROST-OSNT", "title": "Основная теорема арифметики",
                 "description": "Каждое натуральное число > 1 единственным образом (с точностью до порядка) разлагается на простые множители. Виленкин Н.Я. 6 кл., §1.",
                 "examples": [
                     {"uid": "EX-PROST-OSNT-1", "title": "Единственность разложения",
                      "statement": "Разложите 84 на простые множители.",
                      "solution": "84 = 2 · 42 = 2 · 2 · 21 = 2 · 2 · 3 · 7 = 2² · 3 · 7.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 5. Действительные числа (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-DEJSTVITELNYE-CHISLA-b50b77", "SKL-DEJSTVITELNYE-CHISLA-SEED", "Действительные числа",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-DEJSTV-IRRATSION", "title": "Иррациональные числа",
                 "description": "Иррациональное число — бесконечная непериодическая десятичная дробь. √2, √3, π — иррациональные. Доказательство: √2 не представима в виде p/q. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-DEJSTV-IRR-1", "title": "Рациональное или иррациональное",
                      "statement": "Определите тип числа: √9, √7, 0.(3).",
                      "solution": "√9 = 3 — рациональное. √7 ≈ 2.6457... — иррациональное. 0.(3) = 1/3 — рациональное.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-DEJSTV-CHISLOV-PRYAM", "title": "Числовая прямая и полнота",
                 "description": "Каждой точке числовой прямой соответствует единственное действительное число и наоборот. Между рациональными числами существуют иррациональные. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-DEJSTV-PRYAM-1", "title": "Расположение √2 на прямой",
                      "statement": "Между какими целыми числами расположено √5?",
                      "solution": "2² = 4 < 5 < 9 = 3². Значит 2 < √5 < 3. (√5 ≈ 2.236).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-DEJSTV-PRIBLIZH", "title": "Приближение действительных чисел",
                 "description": "Приближение с недостатком/избытком: a ≈ a₀ с точностью до d, если |a − a₀| < d. Мерзляк А.Г. 8 кл.",
                 "examples": [
                     {"uid": "EX-DEJSTV-PRIBL-1", "title": "Приближение √3",
                      "statement": "Найдите √3 с точностью до 0.01.",
                      "solution": "1.73² = 2.9929, 1.74² = 3.0276. 1.73 < √3 < 1.74. Уточняем: 1.732² = 2.999824 ≈ 3. √3 ≈ 1.73.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 6. Комплексные числа (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-KOMPLEKSNYE-CHISLA-89e957", "SKL-KOMPLEKSNYE-CHISLA-SEED", "Комплексные числа",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-KOMPL-ALG-FORMA", "title": "Алгебраическая форма комплексного числа",
                 "description": "z = a + bi, где a = Re(z), b = Im(z), i² = −1. Сложение: (a+bi)+(c+di) = (a+c)+(b+d)i. Умножение: (a+bi)(c+di) = (ac−bd)+(ad+bc)i. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-KOMPL-ALG-1", "title": "Умножение комплексных",
                      "statement": "Вычислите (2 + 3i)(1 − 2i).",
                      "solution": "= 2·1 + 2·(−2i) + 3i·1 + 3i·(−2i) = 2 − 4i + 3i − 6i² = 2 − i + 6 = 8 − i.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-KOMPL-MODUL-ARG", "title": "Модуль и аргумент",
                 "description": "|z| = √(a² + b²). arg(z) = arctg(b/a). Тригонометрическая форма: z = |z|·(cos φ + i sin φ). Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-KOMPL-MOD-1", "title": "Модуль комплексного числа",
                      "statement": "Найдите |3 + 4i|.",
                      "solution": "|3 + 4i| = √(9 + 16) = √25 = 5.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-KOMPL-KORNI", "title": "Извлечение корней из комплексных чисел",
                 "description": "Формула Муавра: zⁿ = rⁿ(cos nφ + i sin nφ). Корень n-й степени: ⁿ√z = ⁿ√r · (cos((φ+2πk)/n) + i sin((φ+2πk)/n)), k=0,1,...,n−1. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-KOMPL-KORN-1", "title": "Корни из −1",
                      "statement": "Найдите все значения √(−1) в комплексных числах.",
                      "solution": "−1 = cos π + i sin π, r = 1. √(−1) = cos(π/2 + πk) + i sin(π/2 + πk). k=0: i. k=1: −i.", "difficulty_level": 3},
                 ]},
            ],
        }],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Алгебра  (15 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _algebra_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Переменные и выражения (7 кл)
    ops += _build_ops_from_topic_def(
        "TOP-PEREMENNYE-I-VYRAZHENIYA-3652b0", "SKL-PEREMENNYE-VYRAZH-SEED", "Переменные и выражения",
        [{
            "uc_min": 7, "uc_max": 7,
            "methods": [
                {"uid": "MET-PER-UPROSCHENIYE", "title": "Упрощение алгебраических выражений",
                 "description": "Приведение подобных слагаемых: 3a + 5a = 8a. Раскрытие скобок: a(b+c) = ab + ac. Макарычев Ю.Н. 7 кл., §1.",
                 "examples": [
                     {"uid": "EX-PER-UPROSCH-1", "title": "Приведение подобных",
                      "statement": "Упростите: 5x − 3y + 2x + 7y.",
                      "solution": "(5x + 2x) + (−3y + 7y) = 7x + 4y.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PER-ZNACHENIE", "title": "Числовое значение выражения",
                 "description": "Подставляем числовые значения переменных и вычисляем по правилам арифметики. Макарычев Ю.Н. 7 кл., §1.",
                 "examples": [
                     {"uid": "EX-PER-ZNACH-1", "title": "Подстановка значений",
                      "statement": "Найдите значение 2a² − 3b при a = 3, b = −2.",
                      "solution": "2 · 9 − 3 · (−2) = 18 + 6 = 24.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PER-TOZHDESTVA", "title": "Тождественные преобразования",
                 "description": "Тождество — равенство, верное при всех допустимых значениях переменных. Тождественное преобразование: замена выражения тождественно равным. Макарычев Ю.Н. 7 кл., §2.",
                 "examples": [
                     {"uid": "EX-PER-TOZHD-1", "title": "Доказательство тождества",
                      "statement": "Докажите, что (a+b)² − (a−b)² = 4ab.",
                      "solution": "Лев. = a²+2ab+b² − (a²−2ab+b²) = a²+2ab+b²−a²+2ab−b² = 4ab. ЧТД.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 2. Многочлены (7-8 кл)
    ops += _build_ops_from_topic_def(
        "TOP-MNOGOCHLENY-0cd461", "SKL-MNOGOCHLENY-SEED", "Многочлены",
        [
            {
                "uc_min": 7, "uc_max": 7,
                "methods": [
                    {"uid": "MET-MNOG-SLOZH-7", "title": "Сложение и вычитание многочленов",
                     "description": "Раскрываем скобки (при вычитании меняем знаки), приводим подобные. Макарычев Ю.Н. 7 кл., §6.",
                     "examples": [
                         {"uid": "EX-MNOG-SLOZH-7-1", "title": "Вычитание многочленов",
                          "statement": "Упростите: (3x² + 2x − 1) − (x² − 4x + 5).",
                          "solution": "3x² + 2x − 1 − x² + 4x − 5 = 2x² + 6x − 6.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-MNOG-UMNOZH-7", "title": "Умножение многочлена на одночлен и многочлен",
                     "description": "Каждый член первого множителя умножаем на каждый член второго. Макарычев Ю.Н. 7 кл., §6.",
                     "examples": [
                         {"uid": "EX-MNOG-UMN-7-1", "title": "Умножение многочленов",
                          "statement": "Раскройте скобки: (x + 3)(2x − 5).",
                          "solution": "2x² − 5x + 6x − 15 = 2x² + x − 15.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-MNOG-FSU-7", "title": "Формулы сокращённого умножения",
                     "description": "(a±b)² = a² ± 2ab + b². a² − b² = (a−b)(a+b). (a±b)³ = a³ ± 3a²b + 3ab² ± b³. a³ ± b³ = (a±b)(a² ∓ ab + b²). Макарычев Ю.Н. 7 кл., §7.",
                     "examples": [
                         {"uid": "EX-MNOG-FSU-7-1", "title": "Разность квадратов",
                          "statement": "Разложите: 25x² − 49y².",
                          "solution": "(5x)² − (7y)² = (5x − 7y)(5x + 7y).", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 8, "uc_max": 8,
                "methods": [
                    {"uid": "MET-MNOG-DELENIE-8", "title": "Деление многочлена на одночлен",
                     "description": "Делим каждый член многочлена на одночлен. Сокращаем степени: aⁿ / aᵐ = aⁿ⁻ᵐ. Макарычев Ю.Н. 8 кл., §1.",
                     "examples": [
                         {"uid": "EX-MNOG-DEL-8-1", "title": "Деление на одночлен",
                          "statement": "Разделите: (12x³ − 8x² + 4x) ÷ (4x).",
                          "solution": "12x³/(4x) − 8x²/(4x) + 4x/(4x) = 3x² − 2x + 1.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-MNOG-GRUPPIROVKA-8", "title": "Разложение группировкой",
                     "description": "Группируем члены попарно, выносим общий множитель из каждой группы, затем выносим общий двучлен. Макарычев Ю.Н. 8 кл., §2.",
                     "examples": [
                         {"uid": "EX-MNOG-GRUPP-8-1", "title": "Группировка",
                          "statement": "Разложите: x³ − 3x² + 2x − 6.",
                          "solution": "x²(x − 3) + 2(x − 3) = (x² + 2)(x − 3).", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-MNOG-GORNER-8", "title": "Теорема Безу и схема Горнера",
                     "description": "Если P(a) = 0, то (x−a) — делитель P(x). Схема Горнера — быстрый способ деления многочлена на (x−a). Мерзляк А.Г. 8 кл.",
                     "examples": [
                         {"uid": "EX-MNOG-GORN-8-1", "title": "Деление по Горнеру",
                          "statement": "Разделите x³ − 6x² + 11x − 6 на (x − 1).",
                          "solution": "P(1) = 1 − 6 + 11 − 6 = 0 ✓. Горнер: 1 | −6 | 11 | −6 → 1 | −5 | 6 | 0. Частное: x² − 5x + 6.", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 3. Линейные уравнения (7 кл)
    ops += _build_ops_from_topic_def(
        "TOP-LINEJNYE-URAVNENIYA-94fc09", "SKL-LINEJNYE-URAVN-SEED", "Линейные уравнения",
        [{
            "uc_min": 7, "uc_max": 7,
            "methods": [
                {"uid": "MET-LIN-PERENOS", "title": "Решение линейного уравнения переносом",
                 "description": "ax + b = 0 → ax = −b → x = −b/a (при a≠0). Переносим слагаемые с x влево, числа вправо, меняя знак. Макарычев Ю.Н. 7 кл., §3.",
                 "examples": [
                     {"uid": "EX-LIN-PEREN-1", "title": "Линейное уравнение",
                      "statement": "Решите: 5x − 7 = 3x + 9.",
                      "solution": "5x − 3x = 9 + 7. 2x = 16. x = 8.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-LIN-SO-SKOBKAMI", "title": "Уравнение со скобками и дробями",
                 "description": "Раскрываем скобки, домножаем на НОЗ для избавления от дробей, приводим подобные. Макарычев Ю.Н. 7 кл., §3.",
                 "examples": [
                     {"uid": "EX-LIN-SKOB-1", "title": "Уравнение с дробями",
                      "statement": "Решите: (x−1)/3 + (x+2)/4 = 2.",
                      "solution": "НОЗ = 12: 4(x−1) + 3(x+2) = 24. 4x−4+3x+6 = 24. 7x+2 = 24. 7x = 22. x = 22/7.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-LIN-CHISLO-RESHENII", "title": "Количество решений линейного уравнения",
                 "description": "ax = b: единственное решение x=b/a (a≠0). 0·x = 0: бесконечно много. 0·x = b (b≠0): нет решений. Макарычев Ю.Н. 7 кл., §3.",
                 "examples": [
                     {"uid": "EX-LIN-CHISLO-1", "title": "Особые случаи",
                      "statement": "Сколько решений: 2(x+3) = 2x + 6?",
                      "solution": "2x + 6 = 2x + 6. 0·x = 0. Бесконечно много решений — тождество.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 4. Системы уравнений (7-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-SISTEMY-URAVNENIJ-118b3a", "SKL-SISTEMY-URAVN-SEED", "Системы уравнений",
        [
            {
                "uc_min": 7, "uc_max": 8,
                "methods": [
                    {"uid": "MET-SIST-PODSTANOVKA-78", "title": "Метод подстановки",
                     "description": "Из одного уравнения выражаем переменную, подставляем в другое. Макарычев Ю.Н. 7 кл., §11.",
                     "examples": [
                         {"uid": "EX-SIST-PODST-78-1", "title": "Подстановка",
                          "statement": "Решите: {x + y = 7, 2x − y = 5}.",
                          "solution": "y = 7 − x. 2x − (7−x) = 5. 3x = 12. x = 4, y = 3.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-SIST-SLOZHENIYE-78", "title": "Метод сложения (алгебраического)",
                     "description": "Уравниваем коэффициенты при одной переменной, складываем/вычитаем уравнения. Макарычев Ю.Н. 7 кл., §11.",
                     "examples": [
                         {"uid": "EX-SIST-SLOZH-78-1", "title": "Метод сложения",
                          "statement": "Решите: {3x + 2y = 16, 5x − 2y = 8}.",
                          "solution": "Складываем: 8x = 24 → x = 3. 3·3 + 2y = 16 → y = 3.5.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-SIST-GRAFICH-78", "title": "Графический метод",
                     "description": "Строим графики обоих уравнений. Точки пересечения — решения системы. Макарычев Ю.Н. 7 кл., §11.",
                     "examples": [
                         {"uid": "EX-SIST-GRAF-78-1", "title": "Графическое решение",
                          "statement": "Решите графически: {y = 2x − 1, y = −x + 5}.",
                          "solution": "2x − 1 = −x + 5 → 3x = 6 → x = 2, y = 3. Точка пересечения (2; 3).", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 9, "uc_max": 9,
                "methods": [
                    {"uid": "MET-SIST-NELINEJN-9", "title": "Нелинейные системы уравнений",
                     "description": "Системы, содержащие квадратные уравнения. Методы: подстановка, замена переменных, сложение. Макарычев Ю.Н. 9 кл., §5.",
                     "examples": [
                         {"uid": "EX-SIST-NELIN-9-1", "title": "Нелинейная система",
                          "statement": "Решите: {x + y = 5, xy = 6}.",
                          "solution": "y = 5 − x. x(5−x) = 6. 5x − x² = 6. x² − 5x + 6 = 0. D=1. x=2,y=3 или x=3,y=2.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-SIST-SIMM-9", "title": "Симметрические системы",
                     "description": "Замена: s = x+y, p = xy. Если система симметрична, выражаем через s и p, затем x,y — корни t² − st + p = 0. Макарычев Ю.Н. 9 кл.",
                     "examples": [
                         {"uid": "EX-SIST-SIMM-9-1", "title": "Симметрическая система",
                          "statement": "Решите: {x² + y² = 25, x + y = 7}.",
                          "solution": "s = 7. x²+y² = (x+y)² − 2xy = 49 − 2p = 25 → p = 12. t²−7t+12=0. t=3,4. (x,y) = (3,4) или (4,3).", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-SIST-KRAMERA-9", "title": "Метод Крамера (определители)",
                     "description": "Для системы 2×2: Δ = a₁b₂−a₂b₁, x = Δx/Δ, y = Δy/Δ. Система совместна при Δ≠0. Мерзляк А.Г. 9 кл.",
                     "examples": [
                         {"uid": "EX-SIST-KRAM-9-1", "title": "Метод Крамера",
                          "statement": "Решите методом Крамера: {2x + 3y = 8, x − y = 1}.",
                          "solution": "Δ = 2·(−1) − 1·3 = −5. Δx = 8·(−1)−1·3 = −11. Δy = 2·1−1·8 = −6. x = 11/5, y = 6/5.", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 5. Линейные неравенства (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-LINEJNYE-NERAVENSTVA-f61cf0", "SKL-LINEJNYE-NERAV-SEED", "Линейные неравенства",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-LINNERAV-RESHENIE", "title": "Решение линейных неравенств",
                 "description": "ax + b > 0. Переносим b: ax > −b. Делим на a. Если a > 0 — знак сохраняется. Если a < 0 — знак меняется. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-LINNERAV-RESH-1", "title": "Линейное неравенство",
                      "statement": "Решите: −3x + 9 > 0.",
                      "solution": "−3x > −9. Делим на −3 (меняем знак): x < 3. Ответ: (−∞; 3).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-LINNERAV-SISTEMA", "title": "Системы линейных неравенств",
                 "description": "Решаем каждое неравенство отдельно. Ответ — пересечение множеств решений. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-LINNERAV-SIST-1", "title": "Система неравенств",
                      "statement": "Решите: {2x − 1 > 3, 5 − x > 0}.",
                      "solution": "2x > 4 → x > 2. −x > −5 → x < 5. Пересечение: 2 < x < 5.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-LINNERAV-DVOINOE", "title": "Двойное неравенство",
                 "description": "a < f(x) < b эквивалентно системе {f(x) > a, f(x) < b}. Можно решать как одно выражение, применяя операции ко всем частям одновременно. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-LINNERAV-DVOIN-1", "title": "Двойное неравенство",
                      "statement": "Решите: −1 ≤ 2x + 3 ≤ 7.",
                      "solution": "−1 − 3 ≤ 2x ≤ 7 − 3. −4 ≤ 2x ≤ 4. −2 ≤ x ≤ 2.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 6. Квадратные уравнения (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-KVADRATNYE-URAVNENIYA-0fdb01", "SKL-KVADRATNYE-URAVN-SEED", "Квадратные уравнения",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-KVUR-DISKRIMINANT", "title": "Решение через дискриминант",
                 "description": "ax² + bx + c = 0. D = b² − 4ac. При D > 0: x = (−b ± √D)/(2a). D = 0: x = −b/(2a). D < 0: нет решений. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-KVUR-DISKR-1", "title": "Решение квадратного уравнения",
                      "statement": "Решите: 2x² − 5x + 2 = 0.",
                      "solution": "D = 25 − 16 = 9. x₁ = (5+3)/4 = 2, x₂ = (5−3)/4 = 0.5.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-KVUR-VIETA", "title": "Теорема Виета",
                 "description": "Для x² + px + q = 0: x₁ + x₂ = −p, x₁ · x₂ = q. Позволяет подбирать корни и проверять решение. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-KVUR-VIETA-1", "title": "Теорема Виета",
                      "statement": "Решите подбором: x² − 7x + 12 = 0.",
                      "solution": "x₁ + x₂ = 7, x₁ · x₂ = 12. Подбор: 3 и 4. Проверка: 3+4=7, 3·4=12 ✓.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-KVUR-NEPOLNOE", "title": "Неполные квадратные уравнения",
                 "description": "ax² + bx = 0: x(ax + b) = 0. ax² + c = 0: x² = −c/a. ax² = 0: x = 0. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-KVUR-NEPOL-1", "title": "Неполное квадратное",
                      "statement": "Решите: 3x² − 12 = 0.",
                      "solution": "3x² = 12. x² = 4. x = ±2.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 7. Дискриминант (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-DISKRIMINANT-4c4ddb", "SKL-DISKRIMINANT-SEED", "Дискриминант",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-DISKR-FORMULA", "title": "Вычисление дискриминанта",
                 "description": "D = b² − 4ac. При D > 0: два корня. D = 0: один корень (кратный). D < 0: нет действительных корней. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-DISKR-FORM-1", "title": "Определение числа корней",
                      "statement": "Не решая, определите число корней: x² + 4x + 5 = 0.",
                      "solution": "D = 16 − 20 = −4 < 0. Действительных корней нет.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-DISKR-CHETVERT", "title": "Формула с D/4 для чётного b",
                 "description": "Если b = 2k: D₁ = k² − ac. x = (−k ± √D₁)/a. Удобнее, когда b чётное. Макарычев Ю.Н. 8 кл., §8.",
                 "examples": [
                     {"uid": "EX-DISKR-CHETV-1", "title": "D/4 для чётного b",
                      "statement": "Решите: x² − 6x + 8 = 0 через D₁.",
                      "solution": "k = 3. D₁ = 9 − 8 = 1. x = (3 ± 1)/1. x₁ = 4, x₂ = 2.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-DISKR-PARAMETR", "title": "Дискриминант в задачах с параметром",
                 "description": "Условие «два корня» → D > 0. «Один корень» → D = 0. «Нет корней» → D < 0. Решаем неравенство относительно параметра. Макарычев Ю.Н. 9 кл.",
                 "examples": [
                     {"uid": "EX-DISKR-PARAM-1", "title": "Задача с параметром",
                      "statement": "При каких значениях k уравнение x² + kx + 4 = 0 имеет два корня?",
                      "solution": "D = k² − 16 > 0. k² > 16. |k| > 4. k ∈ (−∞;−4) ∪ (4;+∞).", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 8. Факторизация (7-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-FAKTORIZATSIYA-060de7", "SKL-FAKTORIZATSIYA-SEED", "Факторизация",
        [
            {
                "uc_min": 7, "uc_max": 8,
                "methods": [
                    {"uid": "MET-FAKT-VYNOS-78", "title": "Вынесение общего множителя",
                     "description": "ab + ac = a(b + c). Находим НОД коэффициентов и наименьшую степень каждой переменной. Макарычев Ю.Н. 7 кл., §7.",
                     "examples": [
                         {"uid": "EX-FAKT-VYN-78-1", "title": "Вынесение множителя",
                          "statement": "Разложите: 12x³y − 8x²y².",
                          "solution": "НОД(12,8) = 4, общие: x², y. 4x²y(3x − 2y).", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-FAKT-FSU-78", "title": "Разложение через ФСУ",
                     "description": "a²−b² = (a−b)(a+b). a³−b³ = (a−b)(a²+ab+b²). a³+b³ = (a+b)(a²−ab+b²). Макарычев Ю.Н. 7 кл., §7.",
                     "examples": [
                         {"uid": "EX-FAKT-FSU-78-1", "title": "Сумма кубов",
                          "statement": "Разложите: 8x³ + 27.",
                          "solution": "(2x)³ + 3³ = (2x+3)(4x²−6x+9).", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-FAKT-GRUPP-78", "title": "Разложение группировкой",
                     "description": "Группируем слагаемые попарно, из каждой пары выносим множитель. Макарычев Ю.Н. 7 кл., §7.",
                     "examples": [
                         {"uid": "EX-FAKT-GRUPP-78-1", "title": "Группировка",
                          "statement": "Разложите: ax − ay + bx − by.",
                          "solution": "a(x−y) + b(x−y) = (a+b)(x−y).", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 9, "uc_max": 9,
                "methods": [
                    {"uid": "MET-FAKT-KVAD-TRICH-9", "title": "Разложение квадратного трёхчлена",
                     "description": "ax² + bx + c = a(x − x₁)(x − x₂), если D ≥ 0. Находим корни через дискриминант. Макарычев Ю.Н. 9 кл., §1.",
                     "examples": [
                         {"uid": "EX-FAKT-KVTR-9-1", "title": "Квадратный трёхчлен",
                          "statement": "Разложите: 2x² − 5x − 3.",
                          "solution": "D = 25+24 = 49. x₁ = 3, x₂ = −0.5. 2(x−3)(x+0.5) = (x−3)(2x+1).", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-FAKT-ZAMENA-9", "title": "Факторизация через замену переменной",
                     "description": "Если выражение биквадратное (ax⁴+bx²+c) или содержит повторяющуюся подструктуру, делаем замену t = x², t = x+1/x и т.д. Макарычев Ю.Н. 9 кл.",
                     "examples": [
                         {"uid": "EX-FAKT-ZAM-9-1", "title": "Биквадратное выражение",
                          "statement": "Разложите: x⁴ − 5x² + 4.",
                          "solution": "t = x². t² − 5t + 4 = (t−1)(t−4) = (x²−1)(x²−4) = (x−1)(x+1)(x−2)(x+2).", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-FAKT-DELENIYE-9", "title": "Факторизация делением (теорема Безу)",
                     "description": "Если P(a) = 0, то P(x) = (x−a)Q(x). Ищем целые корни среди делителей свободного члена. Мерзляк А.Г. 9 кл.",
                     "examples": [
                         {"uid": "EX-FAKT-DEL-9-1", "title": "Корень — делитель свободного члена",
                          "statement": "Разложите: x³ − 3x² − 4x + 12.",
                          "solution": "P(2) = 8−12−8+12 = 0. Делим: x³−3x²−4x+12 = (x−2)(x²−x−6) = (x−2)(x−3)(x+2).", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 9. Квадратные неравенства (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-KVADRATNYE-NERAVENSTVA-f1ebc9", "SKL-KVADRATNYE-NERAV-SEED", "Квадратные неравенства",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-KVNERAV-PARABOLA", "title": "Метод параболы (графический)",
                 "description": "Строим эскиз параболы y = ax²+bx+c. Находим корни. Для ax²+bx+c > 0 (a>0): x < x₁ или x > x₂. Макарычев Ю.Н. 9 кл., §3.",
                 "examples": [
                     {"uid": "EX-KVNERAV-PAR-1", "title": "Метод параболы",
                      "statement": "Решите: x² − 5x + 6 > 0.",
                      "solution": "Корни: x=2, x=3. Парабола вверх. y>0 при x<2 или x>3. Ответ: (−∞;2)∪(3;+∞).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-KVNERAV-INTERVALOV", "title": "Метод интервалов",
                 "description": "Находим корни, расставляем на числовой прямой, определяем знак на каждом интервале подстановкой пробной точки. Макарычев Ю.Н. 9 кл., §3.",
                 "examples": [
                     {"uid": "EX-KVNERAV-INTERV-1", "title": "Метод интервалов",
                      "statement": "Решите: (x+1)(x−3) ≤ 0.",
                      "solution": "Корни: −1, 3. Интервалы: (−∞;−1): +, (−1;3): −, (3;+∞): +. Ответ: [−1; 3].", "difficulty_level": 2},
                 ]},
                {"uid": "MET-KVNERAV-OTRICSAT-D", "title": "Квадратное неравенство при D < 0",
                 "description": "Если D < 0 и a > 0: ax²+bx+c > 0 всегда (нет корней, парабола выше оси). Если a < 0: ax²+bx+c < 0 всегда. Макарычев Ю.Н. 9 кл.",
                 "examples": [
                     {"uid": "EX-KVNERAV-OTRD-1", "title": "D < 0",
                      "statement": "Решите: x² + 2x + 5 > 0.",
                      "solution": "D = 4 − 20 = −16 < 0. a = 1 > 0 → парабола всегда выше оси. Ответ: x ∈ ℝ.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 10. Рациональные уравнения (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-RATSIONALNYE-URAVNENIYA-e5c010", "SKL-RATS-URAVN-SEED", "Рациональные уравнения",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-RATSUR-DROB", "title": "Решение дробно-рациональных уравнений",
                 "description": "P(x)/Q(x) = 0 ⟺ P(x) = 0 и Q(x) ≠ 0. Находим ОДЗ, приводим к общему знаменателю, решаем числитель. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-RATSUR-DROB-1", "title": "Дробно-рациональное уравнение",
                      "statement": "Решите: 2/(x−1) = 3/(x+2).",
                      "solution": "ОДЗ: x≠1, x≠−2. 2(x+2) = 3(x−1). 2x+4 = 3x−3. x = 7 (∈ ОДЗ).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-RATSUR-OBSHCH-ZNAM", "title": "Приведение к общему знаменателю",
                 "description": "Находим НОЗ знаменателей, домножаем каждую дробь, получаем уравнение без дробей. Проверяем корни на ОДЗ. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-RATSUR-OBSH-1", "title": "Общий знаменатель",
                      "statement": "Решите: 1/x + 1/(x+1) = 5/6.",
                      "solution": "НОЗ = 6x(x+1). 6(x+1) + 6x = 5x(x+1). 12x+6 = 5x²+5x. 5x²−7x−6 = 0. D=169. x=2, x=−3/5. Оба ∈ ОДЗ.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-RATSUR-ZAMENA", "title": "Замена переменной в дробных уравнениях",
                 "description": "Если уравнение содержит повторяющееся выражение, делаем замену: t = f(x). Решаем относительно t, затем находим x. Макарычев Ю.Н. 9 кл.",
                 "examples": [
                     {"uid": "EX-RATSUR-ZAM-1", "title": "Замена переменной",
                      "statement": "Решите: x + 4/x = 5.",
                      "solution": "Домножаем на x (x≠0): x² + 4 = 5x. x²−5x+4 = 0. (x−1)(x−4) = 0. x = 1, x = 4.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 11. Рациональные неравенства (9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-RATSIONALNYE-NERAVENSTVA-0c5460", "SKL-RATS-NERAV-SEED", "Рациональные неравенства",
        [{
            "uc_min": 9, "uc_max": 9,
            "methods": [
                {"uid": "MET-RATSNER-METOD-INT", "title": "Обобщённый метод интервалов",
                 "description": "P(x)/Q(x) > 0. Находим нули числителя и знаменателя, отмечаем на прямой (знаменатель — выколотые точки). Определяем знак на интервалах. Макарычев Ю.Н. 9 кл., §3.",
                 "examples": [
                     {"uid": "EX-RATSNER-INT-1", "title": "Метод интервалов для дробей",
                      "statement": "Решите: (x−2)/(x+3) > 0.",
                      "solution": "Нули: x=2 (числ.), x=−3 (знам., выкол.). Знаки: (−∞;−3): +, (−3;2): −, (2;+∞): +. Ответ: (−∞;−3)∪(2;+∞).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-RATSNER-KRATNOST", "title": "Метод интервалов с учётом кратности",
                 "description": "Корень чётной кратности — знак НЕ меняется при прохождении. Нечётной — меняется. Макарычев Ю.Н. 9 кл.",
                 "examples": [
                     {"uid": "EX-RATSNER-KRAT-1", "title": "Кратные корни",
                      "statement": "Решите: (x−1)²(x+2) ≤ 0.",
                      "solution": "(x−1)² ≥ 0 всегда. Знак определяет (x+2). (x−1)²(x+2) ≤ 0 при x+2 ≤ 0 или x=1. Ответ: (−∞;−2] ∪ {1}.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-RATSNER-PEREHOD", "title": "Перенос дроби и сравнение с нулём",
                 "description": "Неравенство f(x)/g(x) ≥ h(x) переводим в (f(x)−h(x)g(x))/g(x) ≥ 0 и применяем метод интервалов. НЕЛЬЗЯ умножать на g(x) — знак неизвестен. Макарычев Ю.Н. 9 кл.",
                 "examples": [
                     {"uid": "EX-RATSNER-PEREH-1", "title": "Перенос в одну сторону",
                      "statement": "Решите: 3/(x−1) ≥ 1.",
                      "solution": "3/(x−1) − 1 ≥ 0. (3−(x−1))/(x−1) ≥ 0. (4−x)/(x−1) ≥ 0. Нули: x=4, x=1 (выкол.). Ответ: (1; 4].", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 12. Неравенства с модулем (9-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-NERAVENSTVA-S-MODULEM-102864", "SKL-NERAV-MODUL-SEED", "Неравенства с модулем",
        [
            {
                "uc_min": 9, "uc_max": 9,
                "methods": [
                    {"uid": "MET-NMOD-OSNOV-9", "title": "Базовые неравенства с модулем",
                     "description": "|f(x)| < a ⟺ −a < f(x) < a (при a>0). |f(x)| > a ⟺ f(x) < −a или f(x) > a. Макарычев Ю.Н. 9 кл.",
                     "examples": [
                         {"uid": "EX-NMOD-OSN-9-1", "title": "Простое неравенство с модулем",
                          "statement": "Решите: |2x − 3| < 5.",
                          "solution": "−5 < 2x−3 < 5. −2 < 2x < 8. −1 < x < 4.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 10, "uc_max": 11,
                "methods": [
                    {"uid": "MET-NMOD-SLOZHNYE-1011", "title": "Сложные неравенства с модулем",
                     "description": "Метод раскрытия модуля: разбиваем на интервалы по точкам, где подмодульные выражения = 0. На каждом раскрываем модуль с нужным знаком. Алимов Ш.А. 10-11 кл.",
                     "examples": [
                         {"uid": "EX-NMOD-SLOZH-1011-1", "title": "Два модуля",
                          "statement": "Решите: |x−1| + |x+2| > 5.",
                          "solution": "Критические точки: −2, 1. На (−∞;−2): (1−x)+(−x−2) = −2x−1 > 5 → x < −3. На [−2;1]: (1−x)+(x+2) = 3 > 5 — неверно. На (1;+∞): (x−1)+(x+2) = 2x+1 > 5 → x > 2. Ответ: (−∞;−3) ∪ (2;+∞).", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-NMOD-METOD-ZAMEN-1011", "title": "Замена переменной с модулем",
                     "description": "Если выражение зависит от |f(x)|, делаем замену t = |f(x)| ≥ 0 и решаем относительно t. Алимов Ш.А. 10-11 кл.",
                     "examples": [
                         {"uid": "EX-NMOD-ZAM-1011-1", "title": "Замена t = |x|",
                          "statement": "Решите: |x|² − 5|x| + 6 < 0.",
                          "solution": "t = |x| ≥ 0. t²−5t+6 < 0. (t−2)(t−3) < 0. 2 < t < 3. 2 < |x| < 3. x ∈ (−3;−2) ∪ (2;3).", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 13. Иррациональные уравнения (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-IRRATSIONALNYE-URAVNENIYA-e5dde5", "SKL-IRRATS-URAVN-SEED", "Иррациональные уравнения",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-IRR-VOZVEDEN", "title": "Возведение в степень",
                 "description": "√f(x) = g(x) ⟺ f(x) = g²(x) и g(x) ≥ 0. Обязательна проверка — могут появиться посторонние корни. Алимов Ш.А. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-IRR-VOZV-1", "title": "Возведение в квадрат",
                      "statement": "Решите: √(2x+1) = x − 1.",
                      "solution": "ОДЗ: x ≥ 1. 2x+1 = (x−1)² = x²−2x+1. x²−4x = 0. x(x−4) = 0. x=0 (не ∈ ОДЗ), x=4. Проверка: √9 = 3 = 4−1 ✓.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-IRR-ZAMENA", "title": "Замена переменной",
                 "description": "При наличии вложенных корней или повторяющихся радикалов: t = √f(x). Получаем алгебраическое уравнение относительно t. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-IRR-ZAM-1", "title": "Замена √x",
                      "statement": "Решите: x − 3√x + 2 = 0.",
                      "solution": "t = √x ≥ 0. t²−3t+2 = 0. (t−1)(t−2) = 0. t=1 → x=1. t=2 → x=4. Проверка: оба верны.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-IRR-SOPRYZH", "title": "Умножение на сопряжённое",
                 "description": "Для √a − √b = c: домножаем на (√a + √b), используя (√a−√b)(√a+√b) = a−b. Мордкович А.Г. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-IRR-SOPR-1", "title": "Сопряжённое",
                      "statement": "Решите: √(x+5) − √(x−3) = 2.",
                      "solution": "Домножим на (√(x+5)+√(x−3)): (x+5)−(x−3) = 2(√(x+5)+√(x−3)). 8 = 2(√(x+5)+√(x−3)). √(x+5)+√(x−3) = 4. Система: сумма=4, разность=2. √(x+5)=3, √(x−3)=1. x=4. Проверка: √9−√1 = 2 ✓.", "difficulty_level": 3},
                 ]},
            ],
        }],
    )

    # 14. Степени (7-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-STEPENI-5a8790", "SKL-STEPENI-SEED", "Степени",
        [
            {
                "uc_min": 7, "uc_max": 7,
                "methods": [
                    {"uid": "MET-STEP-NATURALNAYA-7", "title": "Степень с натуральным показателем",
                     "description": "aⁿ = a · a · ... · a (n раз). a¹ = a, a⁰ = 1 (a≠0). Свойства: aⁿ · aᵐ = aⁿ⁺ᵐ, (aⁿ)ᵐ = aⁿᵐ, (ab)ⁿ = aⁿbⁿ. Макарычев Ю.Н. 7 кл., §4.",
                     "examples": [
                         {"uid": "EX-STEP-NAT-7-1", "title": "Свойства степеней",
                          "statement": "Упростите: 2³ · 2⁴ / 2⁵.",
                          "solution": "2³⁺⁴⁻⁵ = 2² = 4.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 8, "uc_max": 9,
                "methods": [
                    {"uid": "MET-STEP-OTRITS-89", "title": "Степень с отрицательным и нулевым показателем",
                     "description": "a⁰ = 1 (a≠0). a⁻ⁿ = 1/aⁿ (a≠0). Свойства: aⁿ/aᵐ = aⁿ⁻ᵐ. Макарычев Ю.Н. 8 кл., §3.",
                     "examples": [
                         {"uid": "EX-STEP-OTR-89-1", "title": "Отрицательная степень",
                          "statement": "Вычислите: 5⁻² + 2⁻³.",
                          "solution": "1/25 + 1/8 = 8/200 + 25/200 = 33/200 = 0.165.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-STEP-DROBNAYA-89", "title": "Степень с дробным показателем",
                     "description": "a^(m/n) = ⁿ√(aᵐ) (a>0, n∈ℕ, m∈ℤ). Свойства натуральных степеней сохраняются. Мерзляк А.Г. 9 кл.",
                     "examples": [
                         {"uid": "EX-STEP-DRB-89-1", "title": "Дробная степень",
                          "statement": "Вычислите: 8^(2/3).",
                          "solution": "8^(2/3) = (∛8)² = 2² = 4.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-STEP-STANDART-89", "title": "Стандартный вид числа",
                     "description": "a · 10ⁿ, где 1 ≤ a < 10. Используется для записи очень больших и очень малых чисел. Макарычев Ю.Н. 8 кл., §3.",
                     "examples": [
                         {"uid": "EX-STEP-STAND-89-1", "title": "Стандартный вид",
                          "statement": "Запишите в стандартном виде: 0.00056.",
                          "solution": "0.00056 = 5.6 · 10⁻⁴.", "difficulty_level": 1},
                     ]},
                ],
            },
        ],
    )

    # 15. Корни (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-KORNI-542410", "SKL-KORNI-SEED", "Корни",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-KORN-ARIFMET", "title": "Арифметический корень",
                 "description": "√a — неотрицательное число, квадрат которого равен a (a ≥ 0). ⁿ√a — число b ≥ 0: bⁿ = a. Свойства: √(ab) = √a · √b, √(a/b) = √a/√b. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-KORN-ARIF-1", "title": "Свойства корней",
                      "statement": "Упростите: √50 + √32 − √18.",
                      "solution": "5√2 + 4√2 − 3√2 = 6√2.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-KORN-VYNES", "title": "Вынесение множителя из-под корня",
                 "description": "√(a²b) = a√b (a ≥ 0). Раскладываем подкоренное выражение на квадрат и остаток. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-KORN-VYN-1", "title": "Вынесение из-под корня",
                      "statement": "Упростите: √75.",
                      "solution": "√75 = √(25·3) = 5√3.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-KORN-IZBAV", "title": "Избавление от иррациональности в знаменателе",
                 "description": "a/√b = a√b/b. a/(√b ± √c) = a(√b ∓ √c)/(b − c). Домножаем числитель и знаменатель на сопряжённое. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-KORN-IZBAV-1", "title": "Рационализация знаменателя",
                      "statement": "Упростите: 6/(√3 + 1).",
                      "solution": "6(√3−1)/((√3+1)(√3−1)) = 6(√3−1)/(3−1) = 6(√3−1)/2 = 3(√3−1) = 3√3 − 3.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# Proposal builder
# ═══════════════════════════════════════════════════════════════════════════

SECTION_BUILDERS: dict[str, callable] = {
    "arithmetic": _arithmetic_ops,
    "numbers": _numbers_structures_ops,
    "algebra": _algebra_ops,
}


def _make_proposal(ops_fn) -> dict:
    global _OP_COUNTER
    _OP_COUNTER = 0
    ops = ops_fn()
    return {"base_graph_version": 0, "operations": ops}


def build_proposals(section: str | None = None) -> list[dict]:
    if section:
        fn = SECTION_BUILDERS.get(section)
        if not fn:
            print(f"Unknown section: {section}. Available: {', '.join(SECTION_BUILDERS)}", file=sys.stderr)
            sys.exit(1)
        return [_make_proposal(fn)]
    return [_make_proposal(fn) for fn in SECTION_BUILDERS.values()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--section", help=f"Run single section: {', '.join(SECTION_BUILDERS)}")
    parser.add_argument("--kb-url", default="http://localhost:8000")
    parser.add_argument("--tenant-id", default="default")
    args = parser.parse_args()

    proposals = build_proposals(args.section)

    if args.dry_run:
        total_ops = 0
        for i, p in enumerate(proposals, 1):
            n = len(p["operations"])
            total_ops += n
            print(f"Proposal {i}: {n} operations")
            # Show first 3 ops as sample
            for op in p["operations"][:3]:
                print(f"  {op['op_type']} {op.get('target_id', '')} {op.get('properties_delta', {}).get('title', '')}")
            if n > 3:
                print(f"  ... and {n - 3} more")
        print(f"\nTotal: {total_ops} operations across {len(proposals)} proposals")
        return

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
            print(f"  ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
            continue
        data = resp.json()
        items = data.get("items", [])
        if not items:
            print(f"  ERROR: no items in response", file=sys.stderr)
            continue
        proposal_id = items[0].get("proposal_id")
        print(f"  Created: {proposal_id}")

        commit_resp = client.post(f"/v1/proposals/{proposal_id}/commit", headers=headers)
        if commit_resp.status_code == 200:
            ci = commit_resp.json().get("items", [{}])
            if ci and ci[0].get("ok"):
                print(f"  Committed! graph_version={ci[0].get('graph_version')}")
            else:
                print(f"  Commit failed: {ci}", file=sys.stderr)
        else:
            print(f"  ERROR committing: {commit_resp.status_code}", file=sys.stderr)

    client.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
