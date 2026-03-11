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
# SECTION: Функции  (11 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _functions_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Функция как отображение (7-8 кл)
    ops += _build_ops_from_topic_def(
        "TOP-FUNKTSIYA-KAK-OTOBRAZHENIE-1e3bb7", "SKL-FUNKTSIYA-OTOBR-SEED", "Функция как отображение",
        [{
            "uc_min": 7, "uc_max": 8,
            "methods": [
                {"uid": "MET-FUNK-PONYATIE", "title": "Понятие функции",
                 "description": "Функция — правило, по которому каждому x из области определения ставится в соответствие единственное y. Запись: y = f(x). Макарычев Ю.Н. 7 кл., §5.",
                 "examples": [
                     {"uid": "EX-FUNK-PON-1", "title": "Задание функции формулой",
                      "statement": "Дана функция f(x) = 3x − 2. Найдите f(4) и f(−1).",
                      "solution": "f(4) = 3·4 − 2 = 10. f(−1) = 3·(−1) − 2 = −5.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-FUNK-SPOSOBY", "title": "Способы задания функции",
                 "description": "Аналитический (формулой), табличный (таблицей значений), графический (графиком). Макарычев Ю.Н. 7 кл., §5.",
                 "examples": [
                     {"uid": "EX-FUNK-SPOS-1", "title": "Таблица → формула",
                      "statement": "По таблице x: 1,2,3,4; y: 3,5,7,9. Найдите формулу.",
                      "solution": "y увеличивается на 2 при увеличении x на 1. y = 2x + 1. Проверка: 2·1+1=3 ✓, 2·4+1=9 ✓.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-FUNK-ZNACHENIYA", "title": "Нахождение значений функции",
                 "description": "Подставляем значение аргумента в формулу. Для нахождения аргумента по значению функции решаем уравнение f(x) = a. Макарычев Ю.Н. 7 кл., §5.",
                 "examples": [
                     {"uid": "EX-FUNK-ZNACH-1", "title": "Найти x по y",
                      "statement": "f(x) = x² − 4. При каких x f(x) = 12?",
                      "solution": "x² − 4 = 12. x² = 16. x = ±4.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 2. График функции (7-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-GRAFIK-FUNKTSII-61637e", "SKL-GRAFIK-FUNKTSII-SEED", "График функции",
        [
            {
                "uc_min": 7, "uc_max": 8,
                "methods": [
                    {"uid": "MET-GRAF-POSTROENIE-78", "title": "Построение графика по точкам",
                     "description": "Составляем таблицу значений, отмечаем точки на координатной плоскости, соединяем плавной кривой. Макарычев Ю.Н. 7 кл., §5.",
                     "examples": [
                         {"uid": "EX-GRAF-POST-78-1", "title": "График y = x²",
                          "statement": "Постройте график y = x² для x ∈ [−3; 3].",
                          "solution": "Таблица: x: −3,−2,−1,0,1,2,3; y: 9,4,1,0,1,4,9. Парабола с вершиной (0;0), ветви вверх.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-GRAF-CHTENIE-78", "title": "Чтение графика",
                     "description": "По графику определяем: значение функции при данном x, значения x при данном y, нули функции, промежутки знакопостоянства. Макарычев Ю.Н. 7 кл., §5.",
                     "examples": [
                         {"uid": "EX-GRAF-CHTEN-78-1", "title": "Чтение графика",
                          "statement": "По графику y = f(x) определите: f(2), при каких x f(x) = 0.",
                          "solution": "Находим на оси x точку 2, поднимаемся до графика, читаем y. Нули — точки пересечения с осью x.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 9, "uc_max": 9,
                "methods": [
                    {"uid": "MET-GRAF-PREOBR-9", "title": "Преобразования графиков",
                     "description": "y = f(x) + a — сдвиг вверх на a. y = f(x−b) — сдвиг вправо на b. y = kf(x) — растяжение по y в k раз. y = f(kx) — сжатие по x в k раз. y = −f(x) — отражение относительно Ox. Макарычев Ю.Н. 9 кл., §2.",
                     "examples": [
                         {"uid": "EX-GRAF-PREOBR-9-1", "title": "Сдвиги параболы",
                          "statement": "Опишите преобразование: y = (x−2)² + 3 от y = x².",
                          "solution": "Сдвиг вправо на 2 и вверх на 3. Вершина параболы из (0;0) переходит в (2;3).", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-GRAF-KУСОЧН-9", "title": "Кусочно-заданные функции",
                     "description": "Функция задана разными формулами на разных промежутках. Строим каждую часть на своём промежутке. Макарычев Ю.Н. 9 кл.",
                     "examples": [
                         {"uid": "EX-GRAF-KUSOCH-9-1", "title": "Кусочная функция",
                          "statement": "Постройте: f(x) = x² при x < 0; f(x) = 2x при x ≥ 0.",
                          "solution": "Слева от 0 — парабола (ветвь y = x²). Справа от 0 — луч y = 2x. В точке x=0: f(0) = 0 (непрерывно).", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 3. Линейные функции (7 кл)
    ops += _build_ops_from_topic_def(
        "TOP-LINEJNYE-FUNKTSII-270099", "SKL-LINEJNYE-FUNK-SEED", "Линейные функции",
        [{
            "uc_min": 7, "uc_max": 7,
            "methods": [
                {"uid": "MET-LINFUNK-GRAFIK", "title": "График линейной функции",
                 "description": "y = kx + b — прямая. k — угловой коэффициент (наклон), b — свободный член (пересечение с Oy). Для построения достаточно 2 точек. Макарычев Ю.Н. 7 кл., §7.",
                 "examples": [
                     {"uid": "EX-LINFUNK-GRAF-1", "title": "Построение прямой",
                      "statement": "Постройте y = −2x + 3.",
                      "solution": "При x=0: y=3 → точка (0;3). При x=1: y=1 → точка (1;1). Проводим прямую через эти точки.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-LINFUNK-UGLOVOJ", "title": "Угловой коэффициент и взаимное расположение",
                 "description": "k > 0 — возрастает, k < 0 — убывает, k = 0 — горизонтальная. Параллельные: k₁ = k₂. Перпендикулярные: k₁ · k₂ = −1. Макарычев Ю.Н. 7 кл., §7.",
                 "examples": [
                     {"uid": "EX-LINFUNK-UГLOV-1", "title": "Параллельность прямых",
                      "statement": "Параллельны ли y = 3x + 1 и y = 3x − 5?",
                      "solution": "k₁ = 3 = k₂. Прямые параллельны (и не совпадают, т.к. b₁ ≠ b₂).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-LINFUNK-PO-TOCHKAM", "title": "Уравнение прямой по двум точкам",
                 "description": "По точкам (x₁,y₁) и (x₂,y₂): k = (y₂−y₁)/(x₂−x₁), затем b = y₁ − kx₁. Макарычев Ю.Н. 7 кл., §7.",
                 "examples": [
                     {"uid": "EX-LINFUNK-POTOCH-1", "title": "Прямая по двум точкам",
                      "statement": "Найдите уравнение прямой через (1;4) и (3;10).",
                      "solution": "k = (10−4)/(3−1) = 3. b = 4 − 3·1 = 1. y = 3x + 1.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 4. Область определения (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-OBLAST-OPREDELENIYA-e36f26", "SKL-OBLAST-OPRED-SEED", "Область определения",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-OO-DROB", "title": "ОДЗ дробных выражений",
                 "description": "Знаменатель ≠ 0. Для f(x)/g(x): ОДЗ — все x, при которых g(x) ≠ 0. Макарычев Ю.Н. 8 кл., §1.",
                 "examples": [
                     {"uid": "EX-OO-DROB-1", "title": "Область определения дроби",
                      "statement": "Найдите ОО: y = (x+1)/(x² − 4).",
                      "solution": "x² − 4 ≠ 0. x ≠ ±2. ОО: (−∞;−2) ∪ (−2;2) ∪ (2;+∞).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-OO-KOREN", "title": "ОДЗ корневых выражений",
                 "description": "Подкоренное выражение ≥ 0 (для чётного корня). ⁿ√f(x) при чётном n: f(x) ≥ 0. Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-OO-KOREN-1", "title": "Область определения корня",
                      "statement": "Найдите ОО: y = √(3x − 6).",
                      "solution": "3x − 6 ≥ 0. x ≥ 2. ОО: [2; +∞).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-OO-SLOZHNAYA", "title": "ОДЗ составных выражений",
                 "description": "Пересечение всех условий: знаменатель ≠ 0, подкоренное ≥ 0, логарифм от > 0 и т.д. Мерзляк А.Г. 9 кл.",
                 "examples": [
                     {"uid": "EX-OO-SLOZH-1", "title": "Составное выражение",
                      "statement": "Найдите ОО: y = √(x−1) / (x−3).",
                      "solution": "x−1 ≥ 0 → x ≥ 1 и x−3 ≠ 0 → x ≠ 3. ОО: [1;3) ∪ (3;+∞).", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 5. Монотонность (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-MONOTONNOST-dbe010", "SKL-MONOTONNOST-SEED", "Монотонность",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-MONO-OPREDELENIE", "title": "Определение монотонности",
                 "description": "f возрастает на (a;b), если x₁ < x₂ ⇒ f(x₁) < f(x₂). Убывает, если x₁ < x₂ ⇒ f(x₁) > f(x₂). Макарычев Ю.Н. 9 кл., §2.",
                 "examples": [
                     {"uid": "EX-MONO-OPR-1", "title": "Определение по графику",
                      "statement": "Функция f(x) = −x² + 4x. На каких промежутках возрастает?",
                      "solution": "Парабола с вершиной x = −b/(2a) = 2. Возрастает на (−∞; 2], убывает на [2; +∞).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-MONO-DOKAZAT", "title": "Доказательство монотонности",
                 "description": "Берём x₁ < x₂, вычисляем f(x₁) − f(x₂) и определяем знак. Если < 0 — возрастает, > 0 — убывает. Макарычев Ю.Н. 9 кл.",
                 "examples": [
                     {"uid": "EX-MONO-DOK-1", "title": "Доказательство",
                      "statement": "Докажите, что f(x) = 2x + 1 возрастает.",
                      "solution": "f(x₁) − f(x₂) = 2x₁+1 − (2x₂+1) = 2(x₁−x₂). При x₁ < x₂: 2(x₁−x₂) < 0, значит f(x₁) < f(x₂). ЧТД.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-MONO-NAIB-NAIM", "title": "Наибольшее и наименьшее значения",
                 "description": "На отрезке [a;b]: проверяем значения на концах и в вершине (для параболы). Наибольшее — max, наименьшее — min. Мерзляк А.Г. 9 кл.",
                 "examples": [
                     {"uid": "EX-MONO-NAIB-1", "title": "Нахождение max/min",
                      "statement": "Найдите наибольшее значение f(x) = −x² + 6x − 5 на [0; 5].",
                      "solution": "Вершина: x = 3. f(3) = −9+18−5 = 4. f(0) = −5. f(5) = −25+30−5 = 0. Max = 4.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 6. Обратная функция (9-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-OBRATNAYA-FUNKTSIYA-9f767f", "SKL-OBRATN-FUNK-SEED", "Обратная функция",
        [
            {
                "uc_min": 9, "uc_max": 9,
                "methods": [
                    {"uid": "MET-OBRF-PONYATIE-9", "title": "Понятие обратной функции",
                     "description": "Если f — взаимно однозначная (строго монотонная), то существует обратная: f⁻¹. y = f(x) ⟺ x = f⁻¹(y). Графики f и f⁻¹ симметричны относительно y = x. Мерзляк А.Г. 9 кл.",
                     "examples": [
                         {"uid": "EX-OBRF-PON-9-1", "title": "Нахождение обратной",
                          "statement": "Найдите обратную функцию для y = 2x + 3.",
                          "solution": "x = (y−3)/2. Обратная: f⁻¹(y) = (y−3)/2 или y = (x−3)/2.", "difficulty_level": 2},
                     ]},
                ],
            },
            {
                "uc_min": 10, "uc_max": 11,
                "methods": [
                    {"uid": "MET-OBRF-PRIMENENIE-1011", "title": "Обратные тригонометрические и логарифмические функции",
                     "description": "arcsin, arccos, arctg — обратные к sin, cos, tg на соответствующих промежутках. log_a — обратная к aˣ. Алимов Ш.А. 10-11 кл.",
                     "examples": [
                         {"uid": "EX-OBRF-PRIM-1011-1", "title": "Обратная к показательной",
                          "statement": "Какая функция обратна к y = 3ˣ?",
                          "solution": "x = log₃(y). Обратная: y = log₃(x). ОО: x > 0.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-OBRF-GRAFIK-1011", "title": "Построение графика обратной функции",
                     "description": "Отражаем график f относительно прямой y = x. Точка (a;b) на графике f ↔ точка (b;a) на графике f⁻¹. Алимов Ш.А. 10-11 кл.",
                     "examples": [
                         {"uid": "EX-OBRF-GRAF-1011-1", "title": "Симметрия графиков",
                          "statement": "Опишите график обратной функции к y = eˣ.",
                          "solution": "y = ln(x). Кривая проходит через (1;0), возрастает. Симметрична графику y = eˣ относительно y = x.", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 7. Рациональные функции (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-RATSIONALNYE-FUNKTSII-677ea5", "SKL-RATS-FUNK-SEED", "Рациональные функции",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-RATFUNK-GIPERBOLA", "title": "Обратная пропорциональность (гипербола)",
                 "description": "y = k/x — гипербола. При k > 0 — I и III четверти. При k < 0 — II и IV. Асимптоты: оси координат. Макарычев Ю.Н. 8 кл., §6.",
                 "examples": [
                     {"uid": "EX-RATFUNK-GIP-1", "title": "Гипербола",
                      "statement": "Постройте y = 6/x. В каких четвертях?",
                      "solution": "k = 6 > 0 → I и III четверти. Точки: (1;6), (2;3), (3;2), (6;1) и симметричные.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-RATFUNK-DROB-LIN", "title": "Дробно-линейная функция",
                 "description": "y = (ax+b)/(cx+d). Выделяем целую часть: y = a/c + (b−ad/c)/(cx+d). Гипербола со сдвигом. Вертикальная асимптота: cx+d = 0. Макарычев Ю.Н. 9 кл.",
                 "examples": [
                     {"uid": "EX-RATFUNK-DRLIN-1", "title": "Дробно-линейная функция",
                      "statement": "Найдите асимптоты y = (2x+1)/(x−3).",
                      "solution": "Вертикальная: x = 3. Горизонтальная: y = 2/1 = 2 (отношение коэффициентов при x).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-RATFUNK-ISSLED", "title": "Исследование рациональной функции",
                 "description": "ОО (знаменатель ≠ 0), нули (числитель = 0), знак на интервалах, асимптоты, поведение на ±∞. Мерзляк А.Г. 9 кл.",
                 "examples": [
                     {"uid": "EX-RATFUNK-ISSLED-1", "title": "Исследование y = x/(x²−1)",
                      "statement": "Исследуйте: y = x/(x²−1). ОО? Нули? Асимптоты?",
                      "solution": "ОО: x ≠ ±1. Нуль: x = 0. Верт. асимптоты: x = −1, x = 1. Гориз.: y = 0. Нечётная: f(−x) = −f(x).", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 8. Корневые функции (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-KORNEVYE-FUNKTSII-2a9a47", "SKL-KORN-FUNK-SEED", "Корневые функции",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-KORNFUNK-SQRT", "title": "Функция y = √x",
                 "description": "ОО: [0;+∞). ОЗ: [0;+∞). Возрастает. Начальная точка (0;0). Вогнутый (замедляющийся рост). Макарычев Ю.Н. 8 кл., §4.",
                 "examples": [
                     {"uid": "EX-KORNFUNK-SQRT-1", "title": "Свойства √x",
                      "statement": "Найдите ОО и ОЗ y = √(x−2) + 1.",
                      "solution": "x−2 ≥ 0 → x ≥ 2. ОО: [2;+∞). √(x−2) ≥ 0 → y ≥ 1. ОЗ: [1;+∞).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-KORNFUNK-CBRT", "title": "Функция y = ∛x",
                 "description": "ОО: ℝ. ОЗ: ℝ. Нечётная: ∛(−a) = −∛a. Возрастает на всей области. Мерзляк А.Г. 9 кл.",
                 "examples": [
                     {"uid": "EX-KORNFUNK-CBRT-1", "title": "Кубический корень",
                      "statement": "Вычислите: ∛(−27) + ∛8.",
                      "solution": "∛(−27) = −3, ∛8 = 2. −3 + 2 = −1.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-KORNFUNK-PREOBR", "title": "Преобразования корневых функций",
                 "description": "y = a√(x−h) + k — сдвиг на (h;k), растяжение в a раз. При a < 0 — отражение. Мерзляк А.Г. 9 кл.",
                 "examples": [
                     {"uid": "EX-KORNFUNK-PREOBR-1", "title": "Преобразование",
                      "statement": "Опишите преобразование y = −√(x+3) − 1 от y = √x.",
                      "solution": "Сдвиг влево на 3, вниз на 1, отражение относительно Ox. Начальная точка: (−3; −1).", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 9. Степенные функции (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-STEPENNYE-FUNKTSII-9d2782", "SKL-STEP-FUNK-SEED", "Степенные функции",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-STEPFUNK-CELAYA", "title": "Степенная функция y = xⁿ",
                 "description": "При чётном n: ОО=ℝ, чётная, убывает на (−∞;0], возрастает на [0;+∞). При нечётном n: ОО=ℝ, нечётная, возрастает. Алимов Ш.А. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-STEPFUNK-CEL-1", "title": "Сравнение степенных функций",
                      "statement": "Сравните значения x² и x³ при x = 0.5 и x = 2.",
                      "solution": "x=0.5: 0.25 > 0.125 (x² > x³). x=2: 4 < 8 (x² < x³). Смена при x = 1.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-STEPFUNK-DROBNAYA", "title": "Степенная функция y = xᵅ (α дробное)",
                 "description": "y = x^(p/q): ОО зависит от q (чётный/нечётный). x^(1/2) = √x, x^(1/3) = ∛x. Свойства степеней сохраняются. Колмогоров А.Н. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-STEPFUNK-DRB-1", "title": "Дробная степенная функция",
                      "statement": "Найдите ОО и постройте эскиз y = x^(3/2).",
                      "solution": "x^(3/2) = (√x)³. ОО: [0;+∞). Возрастает быстрее √x. f(0)=0, f(1)=1, f(4)=8.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-STEPFUNK-OTRICSAT", "title": "Степенная функция y = x⁻ⁿ",
                 "description": "y = 1/xⁿ. При чётном n: чётная, убывает на (0;+∞). При нечётном n: нечётная. Асимптоты: оси координат. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-STEPFUNK-OTR-1", "title": "y = 1/x²",
                      "statement": "Опишите свойства y = 1/x².",
                      "solution": "ОО: x ≠ 0. Чётная. Убывает на (0;+∞), возрастает на (−∞;0). Горизонт. асимптота y=0, вертик. x=0.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 10. Показательные функции (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-EKSPONENTSIALNYE-FUNKTSII-57a3e0", "SKL-EXP-FUNK-SEED", "Показательные функции",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-EXPFUNK-SVOJSTVA", "title": "Свойства показательной функции",
                 "description": "y = aˣ (a>0, a≠1). ОО=ℝ, ОЗ=(0;+∞). При a>1 — возрастает. При 0<a<1 — убывает. f(0)=1, горизонт. асимптота y=0. Алимов Ш.А. 10-11 кл., §6.",
                 "examples": [
                     {"uid": "EX-EXPFUNK-SV-1", "title": "Свойства 2ˣ",
                      "statement": "Сравните: 2^(√2) и 2^(1.5).",
                      "solution": "√2 ≈ 1.414 < 1.5. Функция 2ˣ возрастает. Значит 2^(√2) < 2^(1.5).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-EXPFUNK-URAVNEN", "title": "Показательные уравнения",
                 "description": "aᶠ⁽ˣ⁾ = aᵍ⁽ˣ⁾ ⟺ f(x) = g(x). Или приводим обе части к одному основанию. Алимов Ш.А. 10-11 кл., §6.",
                 "examples": [
                     {"uid": "EX-EXPFUNK-URAVN-1", "title": "Показательное уравнение",
                      "statement": "Решите: 4ˣ = 8.",
                      "solution": "(2²)ˣ = 2³. 2^(2x) = 2³. 2x = 3. x = 1.5.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-EXPFUNK-NERAVENSTVA", "title": "Показательные неравенства",
                 "description": "При a > 1: aᶠ⁽ˣ⁾ > aᵍ⁽ˣ⁾ ⟺ f(x) > g(x). При 0 < a < 1: знак меняется. Алимов Ш.А. 10-11 кл., §6.",
                 "examples": [
                     {"uid": "EX-EXPFUNK-NERAV-1", "title": "Показательное неравенство",
                      "statement": "Решите: (1/3)ˣ > 9.",
                      "solution": "(1/3)ˣ > (1/3)⁻². Основание 0 < 1/3 < 1 → знак меняется: x < −2.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 11. Логарифмические функции (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea", "SKL-LOG-FUNK-SEED", "Логарифмические функции",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-LOGFUNK-SVOJSTVA", "title": "Свойства логарифмической функции",
                 "description": "y = log_a(x). ОО: (0;+∞). ОЗ: ℝ. При a>1 — возрастает. При 0<a<1 — убывает. log_a(1) = 0, log_a(a) = 1. Вертик. асимптота x=0. Алимов Ш.А. 10-11 кл., §7.",
                 "examples": [
                     {"uid": "EX-LOGFUNK-SV-1", "title": "Вычисление логарифмов",
                      "statement": "Вычислите: log₂(32) + log₃(1/9).",
                      "solution": "log₂(32) = log₂(2⁵) = 5. log₃(1/9) = log₃(3⁻²) = −2. 5 + (−2) = 3.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-LOGFUNK-FORMULY", "title": "Формулы логарифмов",
                 "description": "log(ab) = log a + log b. log(a/b) = log a − log b. log(aⁿ) = n·log a. Формула перехода: log_a(b) = log_c(b)/log_c(a). Алимов Ш.А. 10-11 кл., §7.",
                 "examples": [
                     {"uid": "EX-LOGFUNK-FORM-1", "title": "Применение формул",
                      "statement": "Упростите: log₆(12) + log₆(3).",
                      "solution": "log₆(12·3) = log₆(36) = log₆(6²) = 2.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-LOGFUNK-URAVNEN", "title": "Логарифмические уравнения",
                 "description": "log_a(f(x)) = b ⟺ f(x) = aᵇ (и f(x) > 0). log_a(f(x)) = log_a(g(x)) ⟺ f(x) = g(x), f(x)>0, g(x)>0. Алимов Ш.А. 10-11 кл., §7.",
                 "examples": [
                     {"uid": "EX-LOGFUNK-URAVN-1", "title": "Логарифмическое уравнение",
                      "statement": "Решите: log₂(x+3) = 5.",
                      "solution": "x + 3 = 2⁵ = 32. x = 29. Проверка: 29 + 3 = 32 > 0 ✓.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Тригонометрия  (6 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _trigonometry_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Единичная окружность (9-10 кл)
    ops += _build_ops_from_topic_def(
        "TOP-EDINICHNAYA-OKRUZHNOST-7311af", "SKL-EDINICH-OKRUZH-SEED", "Единичная окружность",
        [{
            "uc_min": 9, "uc_max": 10,
            "methods": [
                {"uid": "MET-EDOKR-OPRED", "title": "Определение sin и cos через единичную окружность",
                 "description": "Точка на единичной окружности с углом α: координаты (cos α; sin α). sin²α + cos²α = 1. Макарычев Ю.Н. 9 кл. + Алимов 10 кл.",
                 "examples": [
                     {"uid": "EX-EDOKR-OPR-1", "title": "Координаты на окружности",
                      "statement": "Найдите sin 30° и cos 30°.",
                      "solution": "sin 30° = 1/2, cos 30° = √3/2. Проверка: (1/2)² + (√3/2)² = 1/4 + 3/4 = 1 ✓.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-EDOKR-ZNAKI", "title": "Знаки тригонометрических функций по четвертям",
                 "description": "I четверть: все +. II: sin +, cos −. III: tg +, остальные −. IV: cos +, sin −. Мнемоника: «Все Студенты Такие Классные». Алимов Ш.А. 10 кл.",
                 "examples": [
                     {"uid": "EX-EDOKR-ZNAK-1", "title": "Знаки в четвертях",
                      "statement": "Определите знак sin 200° и cos 200°.",
                      "solution": "200° — III четверть. sin < 0, cos < 0.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-EDOKR-TABLICH", "title": "Табличные значения тригонометрических функций",
                 "description": "0°: sin=0, cos=1. 30°: 1/2, √3/2. 45°: √2/2, √2/2. 60°: √3/2, 1/2. 90°: 1, 0. Алимов Ш.А. 10 кл., §1.",
                 "examples": [
                     {"uid": "EX-EDOKR-TABL-1", "title": "Табличные значения",
                      "statement": "Вычислите: sin 60° · cos 30° + sin 30° · cos 60°.",
                      "solution": "(√3/2)(√3/2) + (1/2)(1/2) = 3/4 + 1/4 = 1. (Это sin(60°+30°) = sin 90° = 1.)", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 2. Радианная мера (9-10 кл)
    ops += _build_ops_from_topic_def(
        "TOP-RADIANNAYA-MERA-51263f", "SKL-RADIANNAYA-MERA-SEED", "Радианная мера",
        [{
            "uc_min": 9, "uc_max": 10,
            "methods": [
                {"uid": "MET-RAD-PEREVOD", "title": "Перевод градусов в радианы и обратно",
                 "description": "α° = α · π/180 рад. α рад = α · 180/π градусов. π рад = 180°. Алимов Ш.А. 10 кл., §1.",
                 "examples": [
                     {"uid": "EX-RAD-PEREV-1", "title": "Градусы ↔ радианы",
                      "statement": "Переведите 120° в радианы и π/4 в градусы.",
                      "solution": "120° = 120 · π/180 = 2π/3 рад. π/4 = (π/4) · 180/π = 45°.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-RAD-DLINA-DUGI", "title": "Длина дуги и площадь сектора",
                 "description": "Длина дуги: l = rα (α в радианах). Площадь сектора: S = r²α/2. Алимов Ш.А. 10 кл.",
                 "examples": [
                     {"uid": "EX-RAD-DLINA-1", "title": "Длина дуги",
                      "statement": "Найдите длину дуги окружности R=6 с центральным углом 60°.",
                      "solution": "60° = π/3 рад. l = 6 · π/3 = 2π ≈ 6.28.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-RAD-OBSHCH-UGOL", "title": "Углы больше 360° и отрицательные углы",
                 "description": "Углы на единичной окружности: α и α + 2πk дают одну точку. Отрицательные — по часовой стрелке. Алимов Ш.А. 10 кл.",
                 "examples": [
                     {"uid": "EX-RAD-OBSHCH-1", "title": "Приведение угла",
                      "statement": "Найдите sin(13π/6).",
                      "solution": "13π/6 = 2π + π/6. sin(13π/6) = sin(π/6) = 1/2.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 3. Тригонометрические функции (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-TRIGONOMETRICHESKIE-FUNKTSII-84c00c", "SKL-TRIG-FUNK-SEED", "Тригонометрические функции",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-TRIGFUNK-GRAFIKI", "title": "Графики тригонометрических функций",
                 "description": "y = sin x: период 2π, амплитуда 1. y = cos x: то же, сдвиг на π/2. y = tg x: период π, верт. асимптоты x = π/2+πn. Алимов Ш.А. 10-11 кл., §4.",
                 "examples": [
                     {"uid": "EX-TRIGFUNK-GRAF-1", "title": "Период и амплитуда",
                      "statement": "Найдите период и амплитуду y = 3sin(2x).",
                      "solution": "Амплитуда = 3. Период = 2π/2 = π.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TRIGFUNK-FORMULY-PRIVED", "title": "Формулы приведения",
                 "description": "sin(π/2 ± α), cos(π ± α) и т.д. Правило: при π/2 и 3π/2 — функция меняется (sin↔cos), при π и 2π — не меняется. Знак — по исходной четверти. Алимов Ш.А. 10-11 кл., §2.",
                 "examples": [
                     {"uid": "EX-TRIGFUNK-PRIVED-1", "title": "Формула приведения",
                      "statement": "Вычислите sin(π + π/6).",
                      "solution": "sin(π + α) = −sin α. sin(π + π/6) = −sin(π/6) = −1/2.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TRIGFUNK-PREOBR-GRAF", "title": "Преобразования графиков тригонометрических функций",
                 "description": "y = Asin(ωx + φ) + B. A — амплитуда, ω — частота (период = 2π/ω), φ/ω — сдвиг по x, B — сдвиг по y. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-TRIGFUNK-PREOBR-1", "title": "Анализ преобразований",
                      "statement": "Опишите y = 2cos(x − π/3) + 1.",
                      "solution": "Амплитуда 2, период 2π, сдвиг вправо на π/3, вверх на 1. Центральная линия y = 1, макс. y = 3, мин. y = −1.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 4. Тригонометрические тождества (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-TRIGONOMETRICHESKIE-TOZHDESTVA-b4326d", "SKL-TRIG-TOZHD-SEED", "Тригонометрические тождества",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-TRIGTOZH-OSNOV", "title": "Основные тригонометрические тождества",
                 "description": "sin²α + cos²α = 1. tgα = sinα/cosα. 1 + tg²α = 1/cos²α. 1 + ctg²α = 1/sin²α. Алимов Ш.А. 10-11 кл., §2.",
                 "examples": [
                     {"uid": "EX-TRIGTOZH-OSN-1", "title": "Нахождение через тождество",
                      "statement": "sin α = 3/5, α ∈ (0; π/2). Найдите cos α и tg α.",
                      "solution": "cos²α = 1 − 9/25 = 16/25. cos α = 4/5 (I четв., +). tg α = (3/5)/(4/5) = 3/4.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TRIGTOZH-SLOZH", "title": "Формулы сложения",
                 "description": "sin(α±β) = sinα·cosβ ± cosα·sinβ. cos(α±β) = cosα·cosβ ∓ sinα·sinβ. tg(α±β) = (tgα ± tgβ)/(1 ∓ tgα·tgβ). Алимов Ш.А. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-TRIGTOZH-SLOZH-1", "title": "Формула сложения",
                      "statement": "Вычислите cos 75° (без калькулятора).",
                      "solution": "cos 75° = cos(45°+30°) = cos45°cos30° − sin45°sin30° = (√2/2)(√3/2) − (√2/2)(1/2) = (√6−√2)/4.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-TRIGTOZH-DVOJNYE", "title": "Формулы двойного и половинного угла",
                 "description": "sin 2α = 2sinα·cosα. cos 2α = cos²α − sin²α = 1 − 2sin²α = 2cos²α − 1. tg 2α = 2tgα/(1−tg²α). Понижение степени: sin²α = (1−cos2α)/2. Алимов Ш.А. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-TRIGTOZH-DVOJN-1", "title": "Двойной угол",
                      "statement": "Найдите sin 2α, если sin α = 0.6, cos α = 0.8.",
                      "solution": "sin 2α = 2 · 0.6 · 0.8 = 0.96.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 5. Тригонометрические уравнения (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-TRIGONOMETRICHESKIE-URAVNENIYA-37c238", "SKL-TRIG-URAVN-SEED", "Тригонометрические уравнения",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-TRIGUR-PROSTYE", "title": "Простейшие тригонометрические уравнения",
                 "description": "sin x = a: x = (−1)ⁿ arcsin a + πn. cos x = a: x = ±arccos a + 2πn. tg x = a: x = arctg a + πn. Алимов Ш.А. 10-11 кл., §5.",
                 "examples": [
                     {"uid": "EX-TRIGUR-PROST-1", "title": "Простейшее уравнение",
                      "statement": "Решите: cos x = 1/2.",
                      "solution": "x = ±arccos(1/2) + 2πn = ±π/3 + 2πn, n ∈ ℤ.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TRIGUR-ZAMENA", "title": "Сведение к квадратному через замену",
                 "description": "Уравнения вида a·sin²x + b·sinx + c = 0: замена t = sin x. Решаем квадратное, отбираем |t| ≤ 1. Алимов Ш.А. 10-11 кл., §5.",
                 "examples": [
                     {"uid": "EX-TRIGUR-ZAM-1", "title": "Квадратное тригонометрическое",
                      "statement": "Решите: 2cos²x − cosx − 1 = 0.",
                      "solution": "t = cosx. 2t²−t−1 = 0. t = 1, t = −1/2. cos x = 1 → x = 2πn. cos x = −1/2 → x = ±2π/3 + 2πn.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-TRIGUR-ODNOR", "title": "Однородные тригонометрические уравнения",
                 "description": "a·sin²x + b·sinx·cosx + c·cos²x = 0. Делим на cos²x (cos x ≠ 0): a·tg²x + b·tgx + c = 0. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-TRIGUR-ODNOR-1", "title": "Однородное уравнение",
                      "statement": "Решите: sin²x − 3sinx·cosx + 2cos²x = 0.",
                      "solution": "Делим на cos²x: tg²x − 3tgx + 2 = 0. (tgx−1)(tgx−2) = 0. x = π/4+πn, x = arctg2+πn.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 6. Тригонометрические неравенства (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-TRIGONOMETRICHESKIE-NERAVENSTV-a65a77", "SKL-TRIG-NERAV-SEED", "Тригонометрические неравенства",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-TRIGNER-OKRUZHNOST", "title": "Решение через единичную окружность",
                 "description": "sin x > a: находим дугу на окружности, где sin > a (выше горизонтальной линии y = a). cos x < a: аналогично (правее вертикальной линии x = a). Алимов Ш.А. 10-11 кл., §5.",
                 "examples": [
                     {"uid": "EX-TRIGNER-OKR-1", "title": "sin x > 1/2",
                      "statement": "Решите: sin x > 1/2.",
                      "solution": "sin x = 1/2 при x = π/6 и x = 5π/6. sin x > 1/2 между ними: x ∈ (π/6 + 2πn; 5π/6 + 2πn).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-TRIGNER-GRAFICH", "title": "Графический метод",
                 "description": "Строим графики y = f(x) и y = a. Определяем промежутки, где f(x) > a (график выше прямой). Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-TRIGNER-GRAF-1", "title": "Графическое решение",
                      "statement": "Решите: cos x ≥ 0 на [0; 2π].",
                      "solution": "cos x ≥ 0 в I и IV четвертях: [0; π/2] ∪ [3π/2; 2π].", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TRIGNER-SLOZHNYE", "title": "Сложные тригонометрические неравенства",
                 "description": "Приводим к виду с одной функцией (через формулы), затем решаем базовое неравенство. Для tg x > a: x ∈ (arctg a + πn; π/2 + πn). Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-TRIGNER-SLOZH-1", "title": "Неравенство с tg",
                      "statement": "Решите: tg x ≤ 1.",
                      "solution": "tg x = 1 при x = π/4. tg x ≤ 1 на (−π/2 + πn; π/4 + πn], n ∈ ℤ.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Геометрия  (12 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _geometry_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Геометрические фигуры (5-6 кл)
    ops += _build_ops_from_topic_def(
        "TOP-GEOMETRICHESKIE-FIGURY-001", "SKL-GEOM-FIGURY-SEED", "Геометрические фигуры",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-GEOMFIG-KLASSIF", "title": "Классификация геометрических фигур",
                 "description": "Плоские: треугольник, квадрат, прямоугольник, круг, ромб, трапеция, параллелограмм. Объёмные: куб, параллелепипед, цилиндр, конус, сфера. Виленкин Н.Я. 5 кл.",
                 "examples": [
                     {"uid": "EX-GEOMFIG-KLAS-1", "title": "Определение фигуры",
                      "statement": "Фигура имеет 4 стороны, все углы прямые, но стороны не все равны. Как она называется?",
                      "solution": "Прямоугольник. (Если бы все стороны равны — квадрат.)", "difficulty_level": 1},
                 ]},
                {"uid": "MET-GEOMFIG-SIMMETRY", "title": "Симметрия фигур",
                 "description": "Осевая: фигура совпадает сама с собой при отражении. Центральная: при повороте на 180°. Квадрат: 4 оси, центральная. Круг: ∞ осей. Виленкин Н.Я. 6 кл.",
                 "examples": [
                     {"uid": "EX-GEOMFIG-SIMM-1", "title": "Оси симметрии",
                      "statement": "Сколько осей симметрии у равностороннего треугольника?",
                      "solution": "3 оси симметрии (через каждую вершину и середину противоположной стороны).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-GEOMFIG-POSTROENIE", "title": "Построение фигур с помощью циркуля и линейки",
                 "description": "Отрезок, перпендикуляр, биссектриса угла, середина отрезка. Основные построения с циркулем и линейкой. Виленкин Н.Я. 5 кл.",
                 "examples": [
                     {"uid": "EX-GEOMFIG-POST-1", "title": "Построение перпендикуляра",
                      "statement": "Постройте перпендикуляр к прямой из точки, не лежащей на ней.",
                      "solution": "Циркулем из точки засечь прямую в 2 местах. Из них — дуги равного радиуса. Через точку и пересечение дуг — перпендикуляр.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 2. Периметр и площадь (5-6 кл)
    ops += _build_ops_from_topic_def(
        "TOP-PERIMETR-I-PLOSHCHAD-003", "SKL-PERIM-PLOSH-SEED", "Периметр и площадь",
        [{
            "uc_min": 5, "uc_max": 6,
            "methods": [
                {"uid": "MET-PP-PRYAMOUG", "title": "Периметр и площадь прямоугольника",
                 "description": "P = 2(a + b). S = a · b. Для квадрата: P = 4a, S = a². Виленкин Н.Я. 5 кл., §3.",
                 "examples": [
                     {"uid": "EX-PP-PRYAM-1", "title": "Площадь прямоугольника",
                      "statement": "Комната 5 м × 3.5 м. Найдите площадь пола и периметр.",
                      "solution": "S = 5 · 3.5 = 17.5 м². P = 2(5 + 3.5) = 17 м.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PP-TREUGOLNIK", "title": "Площадь треугольника",
                 "description": "S = (a · h)/2, где a — основание, h — высота. Для прямоугольного: S = (a · b)/2 (катеты). Виленкин Н.Я. 5 кл.",
                 "examples": [
                     {"uid": "EX-PP-TREUG-1", "title": "Площадь треугольника",
                      "statement": "Основание 10 см, высота 6 см. Найдите площадь.",
                      "solution": "S = (10 · 6)/2 = 30 см².", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PP-KRUG", "title": "Длина окружности и площадь круга",
                 "description": "Длина: C = 2πr = πd. Площадь: S = πr². π ≈ 3.14. Виленкин Н.Я. 6 кл.",
                 "examples": [
                     {"uid": "EX-PP-KRUG-1", "title": "Площадь круга",
                      "statement": "Радиус круга 7 см. Найдите длину окружности и площадь.",
                      "solution": "C = 2π · 7 = 14π ≈ 43.96 см. S = π · 49 ≈ 153.86 см².", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 3. Точка и прямая (7 кл)
    ops += _build_ops_from_topic_def(
        "TOP-TOCHKA-I-PRYAMAYA-291b4a", "SKL-TOCHKA-PRYAM-SEED", "Точка и прямая",
        [{
            "uc_min": 7, "uc_max": 7,
            "methods": [
                {"uid": "MET-TP-AKSIOMY", "title": "Основные аксиомы геометрии",
                 "description": "Через 2 точки — единственная прямая. На прямой — бесконечно много точек. Через точку вне прямой — единственный перпендикуляр. Атанасян Л.С. 7 кл., §1.",
                 "examples": [
                     {"uid": "EX-TP-AKS-1", "title": "Аксиомы",
                      "statement": "Сколько прямых можно провести через 3 точки, не лежащие на одной прямой?",
                      "solution": "3 прямые: AB, BC, AC.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TP-OTREZOK-LUCH", "title": "Отрезок, луч, угол",
                 "description": "Отрезок AB — часть прямой между A и B. Луч — часть прямой от точки в одну сторону. Угол — два луча с общим началом. Атанасян Л.С. 7 кл., §1.",
                 "examples": [
                     {"uid": "EX-TP-OTR-1", "title": "Точки на отрезке",
                      "statement": "A, B, C на прямой, AB = 5, BC = 3, AC = 8. Какая точка между другими?",
                      "solution": "AB + BC = 5 + 3 = 8 = AC. Значит B между A и C.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TP-PERPENDIK", "title": "Перпендикулярные и параллельные прямые",
                 "description": "a ⊥ b — прямые пересекаются под 90°. a ∥ b — не пересекаются. Признаки параллельности: равенство накрест лежащих углов, соответственных углов. Атанасян Л.С. 7 кл., §2.",
                 "examples": [
                     {"uid": "EX-TP-PERP-1", "title": "Параллельные прямые",
                      "statement": "Секущая пересекает 2 прямые. Накрест лежащие углы 65° и 65°. Параллельны ли прямые?",
                      "solution": "Накрест лежащие углы равны (65° = 65°) — прямые параллельны.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 4. Углы (7 кл)
    ops += _build_ops_from_topic_def(
        "TOP-UGLY-9cbfc3", "SKL-UGLY-SEED", "Углы",
        [{
            "uc_min": 7, "uc_max": 7,
            "methods": [
                {"uid": "MET-UGL-VIDY", "title": "Виды углов и их измерение",
                 "description": "Острый < 90°. Прямой = 90°. Тупой > 90° и < 180°. Развёрнутый = 180°. Смежные: сумма 180°. Вертикальные: равны. Атанасян Л.С. 7 кл., §1.",
                 "examples": [
                     {"uid": "EX-UGL-VIDY-1", "title": "Смежные углы",
                      "statement": "Один из смежных углов 125°. Найдите другой.",
                      "solution": "180° − 125° = 55°.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-UGL-PRI-PARALLEL", "title": "Углы при параллельных прямых и секущей",
                 "description": "Накрест лежащие равны. Соответственные равны. Односторонние: сумма 180°. Атанасян Л.С. 7 кл., §2.",
                 "examples": [
                     {"uid": "EX-UGL-PARALL-1", "title": "Углы при секущей",
                      "statement": "a ∥ b, секущая c. Один из углов 70°. Найдите все 8 углов.",
                      "solution": "4 угла по 70° (соответственные и вертикальные) и 4 угла по 110° (смежные).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-UGL-BISSEKTRISA", "title": "Биссектриса угла",
                 "description": "Биссектриса делит угол пополам. Каждая точка биссектрисы равноудалена от сторон угла. Атанасян Л.С. 7 кл., §1.",
                 "examples": [
                     {"uid": "EX-UGL-BISS-1", "title": "Биссектриса",
                      "statement": "Угол AOB = 84°. OC — биссектриса. Найдите угол AOC.",
                      "solution": "∠AOC = 84° / 2 = 42°.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 5. Треугольники (7-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-TREUGOLNIKI-de676b", "SKL-TREUGOLNIKI-SEED", "Треугольники",
        [
            {
                "uc_min": 7, "uc_max": 8,
                "methods": [
                    {"uid": "MET-TREUG-PRIZN-RAV-78", "title": "Признаки равенства треугольников",
                     "description": "I: по двум сторонам и углу между ними (SAS). II: по стороне и двум прилежащим углам (ASA). III: по трём сторонам (SSS). Атанасян Л.С. 7 кл., §2.",
                     "examples": [
                         {"uid": "EX-TREUG-PRIZN-78-1", "title": "Равенство треугольников",
                          "statement": "AB=DE, BC=EF, ∠B=∠E. Равны ли △ABC и △DEF? По какому признаку?",
                          "solution": "Да, по I признаку (SAS): две стороны и угол между ними равны.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TREUG-SUMMA-UGL-78", "title": "Сумма углов треугольника",
                     "description": "∠A + ∠B + ∠C = 180°. Внешний угол = сумме двух не смежных с ним внутренних. Атанасян Л.С. 7 кл., §3.",
                     "examples": [
                         {"uid": "EX-TREUG-SUMM-78-1", "title": "Третий угол",
                          "statement": "В △ABC ∠A = 45°, ∠B = 70°. Найдите ∠C.",
                          "solution": "∠C = 180° − 45° − 70° = 65°.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-TREUG-PIFAGOR-78", "title": "Теорема Пифагора",
                     "description": "В прямоугольном треугольнике: c² = a² + b², где c — гипотенуза, a, b — катеты. Обратная: если c² = a²+b², то угол против c — прямой. Атанасян Л.С. 8 кл., §4.",
                     "examples": [
                         {"uid": "EX-TREUG-PIFAG-78-1", "title": "Теорема Пифагора",
                          "statement": "Катеты 6 и 8. Найдите гипотенузу.",
                          "solution": "c² = 36 + 64 = 100. c = 10.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 9, "uc_max": 9,
                "methods": [
                    {"uid": "MET-TREUG-SINUS-TEOR-9", "title": "Теорема синусов",
                     "description": "a/sin A = b/sin B = c/sin C = 2R (R — радиус описанной окружности). Атанасян Л.С. 9 кл., §10.",
                     "examples": [
                         {"uid": "EX-TREUG-SIN-9-1", "title": "Теорема синусов",
                          "statement": "В △ABC: a = 10, ∠A = 30°. Найдите радиус описанной окружности.",
                          "solution": "2R = a/sin A = 10/sin 30° = 10/0.5 = 20. R = 10.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-TREUG-COSINUS-TEOR-9", "title": "Теорема косинусов",
                     "description": "c² = a² + b² − 2ab·cos C. Обобщение теоремы Пифагора (при C = 90°: cos 90° = 0). Атанасян Л.С. 9 кл., §10.",
                     "examples": [
                         {"uid": "EX-TREUG-COS-9-1", "title": "Теорема косинусов",
                          "statement": "a = 5, b = 7, ∠C = 60°. Найдите c.",
                          "solution": "c² = 25 + 49 − 2·5·7·cos 60° = 74 − 35 = 39. c = √39 ≈ 6.24.", "difficulty_level": 2},
                     ]},
                    {"uid": "MET-TREUG-PLOSHCHAD-9", "title": "Формулы площади треугольника",
                     "description": "S = ah/2. S = ab·sin C/2. S = √(p(p−a)(p−b)(p−c)) (Герон, p = (a+b+c)/2). S = abc/(4R). S = pr. Атанасян Л.С. 9 кл.",
                     "examples": [
                         {"uid": "EX-TREUG-PLOSH-9-1", "title": "Формула Герона",
                          "statement": "Стороны 5, 6, 7. Найдите площадь.",
                          "solution": "p = (5+6+7)/2 = 9. S = √(9·4·3·2) = √216 = 6√6 ≈ 14.7.", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 6. Окружность (7-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-OKRUZHNOST-926fe8", "SKL-OKRUZHNOST-SEED", "Окружность",
        [
            {
                "uc_min": 7, "uc_max": 8,
                "methods": [
                    {"uid": "MET-OKRUZH-ELEMENTY-78", "title": "Элементы окружности",
                     "description": "Радиус, диаметр (d = 2r), хорда, дуга, касательная (⊥ радиусу в точке касания), секущая. Атанасян Л.С. 7 кл., §4.",
                     "examples": [
                         {"uid": "EX-OKRUZH-ELEM-78-1", "title": "Элементы окружности",
                          "statement": "Радиус 5. Найдите длину наибольшей хорды.",
                          "solution": "Наибольшая хорда — диаметр = 2 · 5 = 10.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 8, "uc_max": 9,
                "methods": [
                    {"uid": "MET-OKRUZH-VPISANNYE-89", "title": "Вписанные и центральные углы",
                     "description": "Центральный угол = дуге. Вписанный угол = половине дуги. Вписанный угол, опирающийся на диаметр = 90°. Атанасян Л.С. 8 кл., §5.",
                     "examples": [
                         {"uid": "EX-OKRUZH-VPIS-89-1", "title": "Вписанный угол",
                          "statement": "Дуга AB = 120°. Найдите вписанный угол ACB.",
                          "solution": "∠ACB = 120°/2 = 60°.", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-OKRUZH-KASAT-89", "title": "Касательная к окружности",
                     "description": "Касательная ⊥ радиусу в точке касания. Отрезки касательных из внешней точки равны. Атанасян Л.С. 8 кл., §5.",
                     "examples": [
                         {"uid": "EX-OKRUZH-KAS-89-1", "title": "Длина касательной",
                          "statement": "Расстояние от точки до центра = 13, радиус = 5. Длина касательной?",
                          "solution": "По Пифагору: d² = 13² − 5² = 169 − 25 = 144. d = 12.", "difficulty_level": 1},
                     ]},
                ],
            },
        ],
    )

    # 7. Площади (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-PLOSCHADI-c811e2", "SKL-PLOSCHADI-SEED", "Площади",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-PLOSH-PARALLELOGR", "title": "Площадь параллелограмма и трапеции",
                 "description": "Параллелограмм: S = ah. Трапеция: S = (a+b)h/2 (a,b — основания). Ромб: S = d₁d₂/2. Атанасян Л.С. 8 кл., §6.",
                 "examples": [
                     {"uid": "EX-PLOSH-PARAL-1", "title": "Площадь трапеции",
                      "statement": "Основания 8 и 12, высота 5. Площадь?",
                      "solution": "S = (8+12)·5/2 = 50.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PLOSH-PRAVIL-MNOG", "title": "Площадь правильного многоугольника",
                 "description": "S = (1/2)·P·a, где P — периметр, a — апофема. Для правильного n-угольника со стороной s: S = (n·s²)/(4·tg(π/n)). Атанасян Л.С. 9 кл.",
                 "examples": [
                     {"uid": "EX-PLOSH-PRAV-1", "title": "Площадь правильного шестиугольника",
                      "statement": "Сторона правильного шестиугольника 4. Площадь?",
                      "solution": "S = (6·16)/(4·tg(π/6)) = 96/(4·√3/3) = 96·3/(4√3) = 72/√3 = 24√3 ≈ 41.6.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-PLOSH-KOORDINAT", "title": "Площадь через координаты",
                 "description": "S = (1/2)|x₁(y₂−y₃) + x₂(y₃−y₁) + x₃(y₁−y₂)| (формула Гаусса для треугольника). Атанасян Л.С. 9 кл.",
                 "examples": [
                     {"uid": "EX-PLOSH-KOORD-1", "title": "Площадь по координатам",
                      "statement": "Вершины: A(1,2), B(4,6), C(7,2). Площадь?",
                      "solution": "S = (1/2)|1(6−2)+4(2−2)+7(2−6)| = (1/2)|4+0−28| = (1/2)·24 = 12.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 8. Подобие (8-9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-PODOBIE-86fb4a", "SKL-PODOBIE-SEED", "Подобие",
        [{
            "uc_min": 8, "uc_max": 9,
            "methods": [
                {"uid": "MET-PODOB-PRIZN", "title": "Признаки подобия треугольников",
                 "description": "I: по двум углам (AA). II: по двум сторонам и углу (SAS~). III: по трём сторонам (SSS~). Коэффициент подобия k = a'/a. Атанасян Л.С. 8 кл., §7.",
                 "examples": [
                     {"uid": "EX-PODOB-PRIZN-1", "title": "Подобие по AA",
                      "statement": "В △ABC и △DEF: ∠A = ∠D = 50°, ∠B = ∠E = 70°. Подобны ли?",
                      "solution": "Два угла равны → △ABC ~ △DEF (по I признаку). ∠C = ∠F = 60°.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-PODOB-KOEFF", "title": "Свойства подобных фигур",
                 "description": "Отношение периметров = k. Отношение площадей = k². Отношение объёмов = k³. Атанасян Л.С. 8 кл., §7.",
                 "examples": [
                     {"uid": "EX-PODOB-KOEFF-1", "title": "Коэффициент подобия",
                      "statement": "△ABC ~ △DEF, k = 3. S_ABC = 18. Найдите S_DEF.",
                      "solution": "S_DEF = S_ABC · k² = 18 · 9 = 162.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-PODOB-SREDNYAYA", "title": "Средняя линия треугольника",
                 "description": "Средняя линия ∥ основанию и равна его половине. Средняя линия трапеции = (a+b)/2. Атанасян Л.С. 8 кл., §7.",
                 "examples": [
                     {"uid": "EX-PODOB-SREDN-1", "title": "Средняя линия",
                      "statement": "В △ABC средняя линия MN ∥ BC. BC = 14. Найдите MN.",
                      "solution": "MN = BC/2 = 14/2 = 7.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 9. Многогранники (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-MNOGOGRANNIKI-dd928d", "SKL-MNOGOGRAN-SEED", "Многогранники",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-MNOG-PRIZMA", "title": "Призма",
                 "description": "Прямая призма: боковые рёбра ⊥ основаниям. S_бок = P·h (периметр × высота). V = S_осн · h. Правильная — основание правильный многоугольник. Атанасян Л.С. 10-11 кл., §2.",
                 "examples": [
                     {"uid": "EX-MNOG-PRIZM-1", "title": "Объём призмы",
                      "statement": "Правильная треугольная призма, сторона основания 6, высота 10. Объём?",
                      "solution": "S_осн = (6²√3)/4 = 9√3. V = 9√3 · 10 = 90√3 ≈ 155.9.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-MNOG-PIRAMIDA", "title": "Пирамида",
                 "description": "V = S_осн · h/3. Правильная пирамида: боковые рёбра равны, апофема — высота боковой грани. S_бок = P·l/2 (l — апофема). Атанасян Л.С. 10-11 кл., §2.",
                 "examples": [
                     {"uid": "EX-MNOG-PIRAM-1", "title": "Объём пирамиды",
                      "statement": "Квадрат в основании, сторона 8, высота 9. Объём?",
                      "solution": "S_осн = 64. V = 64 · 9 / 3 = 192.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-MNOG-EULER", "title": "Формула Эйлера и правильные многогранники",
                 "description": "V − E + F = 2 (вершины − рёбра + грани). 5 правильных: тетраэдр, куб, октаэдр, додекаэдр, икосаэдр. Атанасян Л.С. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-MNOG-EULER-1", "title": "Формула Эйлера",
                      "statement": "У многогранника 12 вершин и 30 рёбер. Сколько граней?",
                      "solution": "F = 2 − V + E = 2 − 12 + 30 = 20.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 10. Прямая и плоскость (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-PRYAMAYA-I-PLOSKOST-1d0194", "SKL-PRYAMAYA-PLOSK-SEED", "Прямая и плоскость в пространстве",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-PRPL-PERPEND", "title": "Перпендикулярность прямой и плоскости",
                 "description": "Прямая ⊥ плоскости, если ⊥ любой прямой в этой плоскости. Достаточно ⊥ двум пересекающимся прямым. Теорема о трёх перпендикулярах. Атанасян Л.С. 10-11 кл., §1.",
                 "examples": [
                     {"uid": "EX-PRPL-PERP-1", "title": "Перпендикуляр к плоскости",
                      "statement": "SA ⊥ плоскости ABC. AB = 4, SA = 3. Найдите SB.",
                      "solution": "△SAB — прямоугольный. SB = √(SA²+AB²) = √(9+16) = 5.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-PRPL-PARALLEL", "title": "Параллельность прямой и плоскости",
                 "description": "Прямая ∥ плоскости, если ∥ какой-либо прямой в этой плоскости. Признак: не лежит в плоскости и ∥ какой-либо прямой в ней. Атанасян Л.С. 10-11 кл., §1.",
                 "examples": [
                     {"uid": "EX-PRPL-PAR-1", "title": "Параллельность",
                      "statement": "ABCD — параллелограмм, S — точка вне плоскости. Докажите SA ∥ плоскости SBC.",
                      "solution": "В плоскости SBC проведём SM ∥ BC (M — середина SB). AD ∥ BC ∥ SM... (нужна средняя линия). AD ∥ BC, AD не лежит в пл. SBC → AD ∥ пл. SBC.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-PRPL-UGOL", "title": "Двугранный угол",
                 "description": "Угол между двумя полуплоскостями с общим ребром. Линейный угол — угол между перпендикулярами к ребру из каждой полуплоскости. Атанасян Л.С. 10-11 кл., §2.",
                 "examples": [
                     {"uid": "EX-PRPL-UGOL-1", "title": "Двугранный угол",
                      "statement": "Основание пирамиды — квадрат, сторона 6, высота 4. Найдите двугранный угол при боковом ребре.",
                      "solution": "Центр основания O, середина стороны M. OM = 3, высота = 4. tg φ = 4/3. φ = arctg(4/3) ≈ 53.1°.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 11. Тела вращения (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-TELA-VRASCHENIYA-722214", "SKL-TELA-VRASH-SEED", "Тела вращения",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-TELV-TSILINDR", "title": "Цилиндр",
                 "description": "S_бок = 2πrh. S_полн = 2πr(r+h). V = πr²h. Осевое сечение — прямоугольник. Атанасян Л.С. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-TELV-TSIL-1", "title": "Объём цилиндра",
                      "statement": "r = 5, h = 8. Найдите объём и боковую поверхность.",
                      "solution": "V = π·25·8 = 200π ≈ 628.3. S_бок = 2π·5·8 = 80π ≈ 251.3.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TELV-KONUS", "title": "Конус",
                 "description": "S_бок = πrl (l — образующая, l² = r² + h²). V = πr²h/3. Атанасян Л.С. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-TELV-KON-1", "title": "Объём конуса",
                      "statement": "r = 3, h = 4. Найдите объём и образующую.",
                      "solution": "l = √(9+16) = 5. V = π·9·4/3 = 12π ≈ 37.7.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-TELV-SFERA", "title": "Сфера и шар",
                 "description": "S_сферы = 4πr². V_шара = (4/3)πr³. Атанасян Л.С. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-TELV-SFER-1", "title": "Объём шара",
                      "statement": "Радиус шара 6. Найдите объём и площадь поверхности.",
                      "solution": "V = (4/3)π·216 = 288π ≈ 904.8. S = 4π·36 = 144π ≈ 452.4.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 12. Объёмы (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-OBYOMY-d44ad9", "SKL-OBYOMY-SEED", "Объёмы",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-OBJ-PRINTSIP", "title": "Принцип Кавальери",
                 "description": "Если сечения двух тел на одной высоте имеют равные площади — объёмы равны. Позволяет вычислять объёмы сложных тел. Атанасян Л.С. 10-11 кл., §3.",
                 "examples": [
                     {"uid": "EX-OBJ-PRINC-1", "title": "Принцип Кавальери",
                      "statement": "Наклонная призма и прямая призма имеют одинаковые основания и высоты. Равны ли их объёмы?",
                      "solution": "Да, по принципу Кавальери: сечения на одной высоте — конгруэнтные параллелограммы.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-OBJ-USECHENNYE", "title": "Объёмы усечённых тел",
                 "description": "Усечённая пирамида: V = h(S₁+S₂+√(S₁S₂))/3. Усечённый конус: V = πh(r₁²+r₂²+r₁r₂)/3. Атанасян Л.С. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-OBJ-USECH-1", "title": "Усечённый конус",
                      "statement": "Усечённый конус: r₁ = 4, r₂ = 2, h = 6. Объём?",
                      "solution": "V = π·6·(16+4+8)/3 = 6π·28/3 = 56π ≈ 175.9.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-OBJ-KOMBINIROV", "title": "Комбинации тел (вписанные и описанные)",
                 "description": "Шар, вписанный в цилиндр: r_ш = r_ц, h = 2r. Шар, описанный вокруг куба: R = a√3/2. Атанасян Л.С. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-OBJ-KOMB-1", "title": "Шар в цилиндре",
                      "statement": "Шар вписан в цилиндр. r = 5. Найдите отношение V_шара/V_цилиндра.",
                      "solution": "V_ш = (4/3)π·125 = 500π/3. V_ц = π·25·10 = 250π. Отношение: 500π/3 / 250π = 2/3.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Аналитическая геометрия  (7 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _analytic_geometry_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Векторы (9-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-VEKTORY-78d40c", "SKL-VEKTORY-SEED", "Векторы",
        [
            {
                "uc_min": 9, "uc_max": 9,
                "methods": [
                    {"uid": "MET-VEKT-OPERATSII-9", "title": "Операции с векторами",
                     "description": "Сложение: ā + b̄ (правило треугольника/параллелограмма). Вычитание: ā − b̄ = ā + (−b̄). Умножение на число: kā. Атанасян Л.С. 9 кл., §9.",
                     "examples": [
                         {"uid": "EX-VEKT-OPER-9-1", "title": "Сложение векторов",
                          "statement": "ā = (3; 2), b̄ = (−1; 4). Найдите ā + b̄ и 2ā − b̄.",
                          "solution": "ā + b̄ = (2; 6). 2ā − b̄ = (6;4) − (−1;4) = (7; 0).", "difficulty_level": 1},
                     ]},
                    {"uid": "MET-VEKT-DLINA-9", "title": "Длина вектора и расстояние",
                     "description": "|ā| = √(x² + y²). Расстояние AB = √((x₂−x₁)² + (y₂−y₁)²). Единичный вектор: ā/|ā|. Атанасян Л.С. 9 кл., §9.",
                     "examples": [
                         {"uid": "EX-VEKT-DLINA-9-1", "title": "Длина вектора",
                          "statement": "Найдите длину вектора (−3; 4).",
                          "solution": "|ā| = √(9 + 16) = √25 = 5.", "difficulty_level": 1},
                     ]},
                ],
            },
            {
                "uc_min": 10, "uc_max": 11,
                "methods": [
                    {"uid": "MET-VEKT-3D-1011", "title": "Векторы в пространстве",
                     "description": "ā = (x;y;z). |ā| = √(x²+y²+z²). Операции покомпонентно. Коллинеарность: ā = λb̄. Компланарность: смешанное произведение = 0. Атанасян Л.С. 10-11 кл., §4.",
                     "examples": [
                         {"uid": "EX-VEKT-3D-1011-1", "title": "Вектор в пространстве",
                          "statement": "A(1;2;3), B(4;6;3). Найдите AB̄ и |AB̄|.",
                          "solution": "AB̄ = (3;4;0). |AB̄| = √(9+16+0) = 5.", "difficulty_level": 2},
                     ]},
                ],
            },
        ],
    )

    # 2. Декартовы координаты (9 кл)
    ops += _build_ops_from_topic_def(
        "TOP-DEKARTOVY-KOORDINATY-19b067", "SKL-DEKART-KOORD-SEED", "Декартовы координаты",
        [{
            "uc_min": 9, "uc_max": 9,
            "methods": [
                {"uid": "MET-DEKART-SEREDINA", "title": "Координаты середины отрезка",
                 "description": "M = ((x₁+x₂)/2; (y₁+y₂)/2). Делит отрезок пополам. Атанасян Л.С. 9 кл., §9.",
                 "examples": [
                     {"uid": "EX-DEKART-SER-1", "title": "Середина отрезка",
                      "statement": "A(2;5), B(8;1). Найдите середину AB.",
                      "solution": "M = ((2+8)/2; (5+1)/2) = (5; 3).", "difficulty_level": 1},
                 ]},
                {"uid": "MET-DEKART-RASSTOYANIE", "title": "Расстояние между точками",
                 "description": "d = √((x₂−x₁)² + (y₂−y₁)²). Атанасян Л.С. 9 кл., §9.",
                 "examples": [
                     {"uid": "EX-DEKART-RAST-1", "title": "Расстояние",
                      "statement": "A(1;3), B(4;7). Найдите AB.",
                      "solution": "AB = √(9+16) = 5.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-DEKART-DELENIE", "title": "Деление отрезка в данном отношении",
                 "description": "Точка M делит AB в отношении m:n: M = ((nx₁+mx₂)/(m+n); (ny₁+my₂)/(m+n)). Атанасян Л.С. 9 кл.",
                 "examples": [
                     {"uid": "EX-DEKART-DEL-1", "title": "Деление в отношении",
                      "statement": "A(1;2), B(7;8). Точка M делит AB в отношении 1:2 от A. Найдите M.",
                      "solution": "M = ((2·1+1·7)/3; (2·2+1·8)/3) = (9/3; 12/3) = (3; 4).", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 3. Скалярное произведение (9-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-SKALYARNOE-PROIZVEDENIE-5c6f65", "SKL-SKALYAR-PROIZ-SEED", "Скалярное произведение",
        [{
            "uc_min": 9, "uc_max": 11,
            "methods": [
                {"uid": "MET-SKAL-FORMULA", "title": "Формулы скалярного произведения",
                 "description": "ā·b̄ = |ā|·|b̄|·cos φ = x₁x₂+y₁y₂ (2D) = x₁x₂+y₁y₂+z₁z₂ (3D). cos φ = (ā·b̄)/(|ā|·|b̄|). Атанасян Л.С. 9 кл., §9.",
                 "examples": [
                     {"uid": "EX-SKAL-FORM-1", "title": "Угол между векторами",
                      "statement": "ā = (1;2), b̄ = (3;−1). Найдите угол.",
                      "solution": "ā·b̄ = 3−2 = 1. |ā|=√5, |b̄|=√10. cos φ = 1/√50 = 1/(5√2). φ ≈ 81.9°.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-SKAL-ORTOGON", "title": "Перпендикулярность через скалярное произведение",
                 "description": "ā ⊥ b̄ ⟺ ā·b̄ = 0. Проекция ā на b̄: proj_b̄ ā = (ā·b̄)/|b̄|. Атанасян Л.С. 9-11 кл.",
                 "examples": [
                     {"uid": "EX-SKAL-ORTOG-1", "title": "Перпендикулярность",
                      "statement": "При каком k векторы (2;k) и (3;−6) перпендикулярны?",
                      "solution": "2·3 + k·(−6) = 0. 6 − 6k = 0. k = 1.", "difficulty_level": 1},
                 ]},
            ],
        }],
    )

    # 4. Уравнение прямой (9-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-URAVNENIE-PRYAMOJ-f56905", "SKL-URAVN-PRYAMOJ-SEED", "Уравнение прямой",
        [{
            "uc_min": 9, "uc_max": 11,
            "methods": [
                {"uid": "MET-URPR-OBSHCHEE", "title": "Общее уравнение прямой",
                 "description": "Ax + By + C = 0. Нормаль n̄ = (A; B). Направляющий вектор d̄ = (−B; A). Расстояние от точки (x₀;y₀): |Ax₀+By₀+C|/√(A²+B²). Атанасян Л.С. 9 кл.",
                 "examples": [
                     {"uid": "EX-URPR-OBSH-1", "title": "Расстояние от точки до прямой",
                      "statement": "Прямая 3x + 4y − 12 = 0. Расстояние от (1;1)?",
                      "solution": "d = |3+4−12|/√(9+16) = 5/5 = 1.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-URPR-KANON", "title": "Каноническое и параметрическое уравнение",
                 "description": "Каноническое: (x−x₀)/l = (y−y₀)/m (d̄ = (l;m)). Параметрическое: x = x₀+lt, y = y₀+mt. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-URPR-KAN-1", "title": "Параметрическое уравнение",
                      "statement": "Прямая через (2;3) с направляющим (1;−2). Запишите параметрически.",
                      "solution": "x = 2 + t, y = 3 − 2t.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 5. Уравнение окружности (9-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-URAVNENIE-OKRUZHNOSTI-9f8fcf", "SKL-URAVN-OKRUZH-SEED", "Уравнение окружности",
        [{
            "uc_min": 9, "uc_max": 11,
            "methods": [
                {"uid": "MET-UROKR-KANON", "title": "Каноническое уравнение окружности",
                 "description": "(x−a)² + (y−b)² = r². Центр (a;b), радиус r. Общее: x²+y²+Dx+Ey+F=0, центр (−D/2; −E/2), r = √(D²/4+E²/4−F). Атанасян Л.С. 9 кл.",
                 "examples": [
                     {"uid": "EX-UROKR-KAN-1", "title": "Уравнение окружности",
                      "statement": "Центр (2;−3), r = 4. Запишите уравнение.",
                      "solution": "(x−2)² + (y+3)² = 16.", "difficulty_level": 1},
                 ]},
                {"uid": "MET-UROKR-VZAIMN", "title": "Взаимное расположение прямой и окружности",
                 "description": "d < r — 2 точки (секущая). d = r — 1 точка (касательная). d > r — нет общих точек. d — расстояние от центра до прямой. Атанасян Л.С. 9 кл.",
                 "examples": [
                     {"uid": "EX-UROKR-VZAIMN-1", "title": "Прямая и окружность",
                      "statement": "Окружность x² + y² = 25. Прямая 3x + 4y = 25. Касается или пересекает?",
                      "solution": "d = |0+0−25|/5 = 5 = r. Касательная.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 6. Кривые второго порядка (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-KRIVYE-VTOROGO-PORYADKA-6f671e", "SKL-KRIVYE-2-SEED", "Кривые второго порядка",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-KRIV2-ELLIPS", "title": "Эллипс",
                 "description": "x²/a² + y²/b² = 1 (a > b). Фокусы: (±c; 0), c² = a² − b². Сумма расстояний до фокусов = 2a. Эксцентриситет e = c/a. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-KRIV2-ELL-1", "title": "Эллипс",
                      "statement": "x²/25 + y²/9 = 1. Найдите фокусы.",
                      "solution": "a=5, b=3. c² = 25−9 = 16. c = 4. Фокусы: (±4; 0).", "difficulty_level": 2},
                 ]},
                {"uid": "MET-KRIV2-GIPERBOLA", "title": "Гипербола",
                 "description": "x²/a² − y²/b² = 1. Фокусы (±c;0), c² = a²+b². Асимптоты: y = ±(b/a)x. Разность расстояний до фокусов = 2a. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-KRIV2-GIP-1", "title": "Гипербола",
                      "statement": "x²/16 − y²/9 = 1. Найдите асимптоты.",
                      "solution": "a=4, b=3. Асимптоты: y = ±(3/4)x.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-KRIV2-PARABOLA-ANAL", "title": "Парабола (аналитическая)",
                 "description": "y² = 2px — парабола с осью Ox, фокус (p/2; 0), директриса x = −p/2. x² = 2py — с осью Oy. Алимов Ш.А. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-KRIV2-PAR-1", "title": "Парабола",
                      "statement": "y² = 12x. Найдите фокус и директрису.",
                      "solution": "2p = 12, p = 6. Фокус: (3; 0). Директриса: x = −3.", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    # 7. Плоскость в пространстве (10-11 кл)
    ops += _build_ops_from_topic_def(
        "TOP-PLOSKOST-V-PROSTRANSTVE-f03ae1", "SKL-PLOSKOST-PROSTR-SEED", "Плоскость в пространстве",
        [{
            "uc_min": 10, "uc_max": 11,
            "methods": [
                {"uid": "MET-PLPR-URAVNENIE", "title": "Уравнение плоскости",
                 "description": "Ax + By + Cz + D = 0. Нормаль n̄ = (A;B;C). Через 3 точки: составляем систему или используем определитель. Расстояние от точки: |Ax₀+By₀+Cz₀+D|/√(A²+B²+C²). Атанасян Л.С. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-PLPR-URAVN-1", "title": "Уравнение плоскости",
                      "statement": "Плоскость 2x − y + 3z − 6 = 0. Расстояние от O(0;0;0)?",
                      "solution": "d = |0−0+0−6|/√(4+1+9) = 6/√14 ≈ 1.60.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-PLPR-UGOL-PLOSKOSTEJ", "title": "Угол между плоскостями",
                 "description": "cos φ = |n̄₁·n̄₂|/(|n̄₁|·|n̄₂|). Параллельны: n̄₁ ∥ n̄₂. Перпендикулярны: n̄₁·n̄₂ = 0. Атанасян Л.С. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-PLPR-UGOL-1", "title": "Угол между плоскостями",
                      "statement": "Плоскости: x+y+z=0 и x−y=0. Найдите угол.",
                      "solution": "n̄₁=(1;1;1), n̄₂=(1;−1;0). cos φ = |1−1+0|/(√3·√2) = 0. φ = 90°.", "difficulty_level": 2},
                 ]},
                {"uid": "MET-PLPR-PRYAMAYA-PLOSKOST", "title": "Прямая в пространстве и пересечение с плоскостью",
                 "description": "Прямая: (x−x₀)/l = (y−y₀)/m = (z−z₀)/n. Подставляем параметрическое в уравнение плоскости, находим t. Атанасян Л.С. 10-11 кл.",
                 "examples": [
                     {"uid": "EX-PLPR-PRPL-1", "title": "Пересечение прямой и плоскости",
                      "statement": "Прямая: x=1+t, y=2t, z=3−t. Плоскость: x+y+z=6. Точка?",
                      "solution": "(1+t)+2t+(3−t) = 6. 4+2t = 6. t = 1. Точка: (2; 2; 2).", "difficulty_level": 2},
                 ]},
            ],
        }],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Математический анализ  (8 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _analysis_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Предел последовательности
    ops += _build_ops_from_topic_def(
        "TOP-PREDEL-POSLEDOVATELNOSTI-248f64", "SKL-PREDEL-POSL-SEED", "Предел последовательности",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-PREDPOSL-OPRED", "title": "Определение предела последовательности",
             "description": "lim aₙ = a, если для любого ε>0 существует N: при n>N |aₙ−a|<ε. Конечный предел → последовательность сходится. Колмогоров А.Н. 10-11 кл., §8.",
             "examples": [{"uid": "EX-PREDPOSL-OPR-1", "title": "Предел дроби", "statement": "Найдите lim (3n+1)/(n+2) при n→∞.", "solution": "Делим на n: (3+1/n)/(1+2/n) → 3/1 = 3.", "difficulty_level": 2}]},
            {"uid": "MET-PREDPOSL-ARIFM", "title": "Арифметика пределов",
             "description": "lim(aₙ ± bₙ) = lim aₙ ± lim bₙ. lim(aₙ·bₙ) = lim aₙ · lim bₙ. lim(aₙ/bₙ) = lim aₙ / lim bₙ (если ≠0). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PREDPOSL-ARIF-1", "title": "Предел суммы", "statement": "lim (1/n + 2/n²) при n→∞.", "solution": "lim 1/n = 0, lim 2/n² = 0. Ответ: 0.", "difficulty_level": 1}]},
            {"uid": "MET-PREDPOSL-NEOPREDELENNOST", "title": "Раскрытие неопределённостей",
             "description": "∞/∞: делим на старшую степень n. ∞−∞: домножаем на сопряжённое или приводим к общему знаменателю. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PREDPOSL-NEOPR-1", "title": "∞/∞", "statement": "lim (n²+3n)/(2n²−1).", "solution": "Делим на n²: (1+3/n)/(2−1/n²) → 1/2.", "difficulty_level": 2}]},
        ]}],
    )

    # 2. Предел функции
    ops += _build_ops_from_topic_def(
        "TOP-PREDEL-FUNKTSII-1925e2", "SKL-PREDEL-FUNK-SEED", "Предел функции",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-PREDFUNK-ZAMECH", "title": "Первый замечательный предел",
             "description": "lim sin x / x = 1 при x→0. Следствия: lim tg x / x = 1, lim (1−cos x)/x² = 1/2. Колмогоров А.Н. 10-11 кл., §9.",
             "examples": [{"uid": "EX-PREDFUNK-ZAM-1", "title": "Первый замечательный", "statement": "lim sin(3x)/(5x) при x→0.", "solution": "= (3/5) · lim sin(3x)/(3x) = (3/5) · 1 = 3/5.", "difficulty_level": 2}]},
            {"uid": "MET-PREDFUNK-ZAMECH2", "title": "Второй замечательный предел",
             "description": "lim (1+1/n)ⁿ = e при n→∞. lim (1+α/n)ⁿ = eᵅ. Число e ≈ 2.718. Колмогоров А.Н. 10-11 кл., §9.",
             "examples": [{"uid": "EX-PREDFUNK-ZAM2-1", "title": "Второй замечательный", "statement": "lim (1+3/n)ⁿ при n→∞.", "solution": "= e³ ≈ 20.09.", "difficulty_level": 2}]},
            {"uid": "MET-PREDFUNK-NEPRER", "title": "Непрерывность функции",
             "description": "f непрерывна в x₀, если lim f(x) = f(x₀) при x→x₀. Точки разрыва: устранимый, скачок, бесконечный. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PREDFUNK-NEPR-1", "title": "Точка разрыва", "statement": "f(x) = (x²−4)/(x−2). Какой разрыв при x=2?", "solution": "f(x) = (x−2)(x+2)/(x−2) = x+2 при x≠2. lim = 4, но f(2) не определена. Устранимый разрыв.", "difficulty_level": 2}]},
        ]}],
    )

    # 3. Производная
    ops += _build_ops_from_topic_def(
        "TOP-PROIZVODNAYA-cfd26d", "SKL-PROIZVODNAYA-SEED", "Производная",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-PROIZ-OPRED", "title": "Определение производной",
             "description": "f'(x₀) = lim (f(x₀+Δx)−f(x₀))/Δx при Δx→0. Геометрический смысл: угловой коэффициент касательной. Физический: мгновенная скорость. Колмогоров А.Н. 10-11 кл., §9.",
             "examples": [{"uid": "EX-PROIZ-OPR-1", "title": "Производная по определению", "statement": "Найдите (x²)' по определению.", "solution": "lim ((x+Δx)²−x²)/Δx = lim (2xΔx+Δx²)/Δx = lim (2x+Δx) = 2x.", "difficulty_level": 2}]},
            {"uid": "MET-PROIZ-TABLITSA", "title": "Таблица производных",
             "description": "(xⁿ)' = nxⁿ⁻¹. (eˣ)' = eˣ. (aˣ)' = aˣ ln a. (ln x)' = 1/x. (sin x)' = cos x. (cos x)' = −sin x. (tg x)' = 1/cos²x. Колмогоров А.Н. 10-11 кл., §10.",
             "examples": [{"uid": "EX-PROIZ-TABL-1", "title": "Табличные производные", "statement": "Найдите (3x⁴ − 2sin x + eˣ)'.", "solution": "12x³ − 2cos x + eˣ.", "difficulty_level": 1}]},
            {"uid": "MET-PROIZ-KASATELNAYA", "title": "Уравнение касательной",
             "description": "y = f(x₀) + f'(x₀)(x − x₀). Угловой коэффициент k = f'(x₀). Нормаль: k_норм = −1/k. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PROIZ-KAS-1", "title": "Касательная", "statement": "f(x) = x² − 3x. Касательная в x₀ = 2.", "solution": "f(2) = 4−6 = −2. f'(x) = 2x−3, f'(2) = 1. y = −2 + 1·(x−2) = x − 4.", "difficulty_level": 2}]},
        ]}],
    )

    # 4. Правила дифференцирования
    ops += _build_ops_from_topic_def(
        "TOP-PRAVILA-DIFFERENTSIROVANIYA-3bd912", "SKL-PRAVILA-DIFF-SEED", "Правила дифференцирования",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-DIFF-PROIZVEDEN", "title": "Производная произведения и частного",
             "description": "(fg)' = f'g + fg'. (f/g)' = (f'g − fg')/g². Колмогоров А.Н. 10-11 кл., §10.",
             "examples": [{"uid": "EX-DIFF-PROIZ-1", "title": "Производная произведения", "statement": "(x² · sin x)' = ?", "solution": "2x·sin x + x²·cos x.", "difficulty_level": 1}]},
            {"uid": "MET-DIFF-SLOZHNAYA", "title": "Производная сложной функции",
             "description": "(f(g(x)))' = f'(g(x)) · g'(x). Цепное правило: дифференцируем «внешнюю» по «внутренней», умножаем на производную «внутренней». Колмогоров А.Н. 10-11 кл., §10.",
             "examples": [{"uid": "EX-DIFF-SLOZH-1", "title": "Сложная функция", "statement": "(sin(3x²))' = ?", "solution": "cos(3x²) · 6x = 6x·cos(3x²).", "difficulty_level": 2}]},
            {"uid": "MET-DIFF-LOGARIFM", "title": "Логарифмическое дифференцирование",
             "description": "Для y = f(x)^g(x): ln y = g(x)·ln f(x). y'/y = g'·ln f + g·f'/f. Удобно для степенно-показательных. Мордкович А.Г. 10-11 кл.",
             "examples": [{"uid": "EX-DIFF-LOG-1", "title": "Логарифмическое дифференцирование", "statement": "(xˣ)' = ?", "solution": "ln y = x ln x. y'/y = ln x + 1. y' = xˣ(ln x + 1).", "difficulty_level": 3}]},
        ]}],
    )

    # 5. Исследование функций
    ops += _build_ops_from_topic_def(
        "TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f", "SKL-ISSLED-FUNK-SEED", "Исследование функций",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-ISSLED-EKSTREMUM", "title": "Нахождение экстремумов",
             "description": "f'(x₀) = 0 — критическая точка. Если f' меняет знак + → − : максимум. − → + : минимум. Или f''(x₀) < 0 → max, f''(x₀) > 0 → min. Колмогоров А.Н. 10-11 кл., §11.",
             "examples": [{"uid": "EX-ISSLED-EKSTR-1", "title": "Экстремумы", "statement": "f(x) = x³ − 3x. Найдите экстремумы.", "solution": "f' = 3x²−3 = 0 → x = ±1. f''=6x. f''(1)=6>0 → min f(1)=−2. f''(−1)=−6<0 → max f(−1)=2.", "difficulty_level": 2}]},
            {"uid": "MET-ISSLED-VOZVYP", "title": "Выпуклость и точки перегиба",
             "description": "f'' > 0 — выпукла вниз (вогнутая). f'' < 0 — выпукла вверх. Точка перегиба: f'' меняет знак. Колмогоров А.Н. 10-11 кл., §11.",
             "examples": [{"uid": "EX-ISSLED-VOZV-1", "title": "Точка перегиба", "statement": "f(x) = x³ − 6x² + 12x. Точка перегиба?", "solution": "f'' = 6x − 12 = 0 → x = 2. f''(1) = −6 < 0, f''(3) = 6 > 0. Перегиб в x = 2, f(2) = 8.", "difficulty_level": 2}]},
            {"uid": "MET-ISSLED-NAIB-NAIM", "title": "Наибольшее и наименьшее на отрезке",
             "description": "На [a;b]: находим f'(x) = 0, проверяем f(a), f(b) и f в критических точках. Наибольшее/наименьшее среди них. Колмогоров А.Н. 10-11 кл., §11.",
             "examples": [{"uid": "EX-ISSLED-NAIB-1", "title": "Max/min на отрезке", "statement": "f(x) = x³ − 3x + 2 на [−2; 2].", "solution": "f' = 3x²−3 = 0 → x = ±1. f(−2)=0, f(−1)=4, f(1)=0, f(2)=4. Max=4, min=0.", "difficulty_level": 2}]},
        ]}],
    )

    # 6. Первообразная
    ops += _build_ops_from_topic_def(
        "TOP-PERVOOBRAZNAYA-e23096", "SKL-PERVOOBRAZNAYA-SEED", "Первообразная",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-PERVOOBR-TABL", "title": "Таблица первообразных",
             "description": "∫xⁿdx = xⁿ⁺¹/(n+1)+C. ∫eˣdx = eˣ+C. ∫cos x dx = sin x+C. ∫sin x dx = −cos x+C. ∫dx/x = ln|x|+C. Колмогоров А.Н. 10-11 кл., §12.",
             "examples": [{"uid": "EX-PERVOOBR-TABL-1", "title": "Таблица первообразных", "statement": "Найдите ∫(3x² + cos x)dx.", "solution": "x³ + sin x + C.", "difficulty_level": 1}]},
            {"uid": "MET-PERVOOBR-ZAMENA", "title": "Метод подстановки",
             "description": "∫f(g(x))g'(x)dx = F(g(x))+C. Замена u = g(x), du = g'(x)dx. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PERVOOBR-ZAM-1", "title": "Подстановка", "statement": "∫sin(3x)dx.", "solution": "u=3x, du=3dx. (1/3)∫sin u du = −cos(3x)/3 + C.", "difficulty_level": 2}]},
            {"uid": "MET-PERVOOBR-NACHUSLOV", "title": "Задача Коши (начальное условие)",
             "description": "F(x) = ∫f(x)dx + C. Начальное условие F(x₀) = y₀ определяет C. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PERVOOBR-NACH-1", "title": "Задача Коши", "statement": "F'(x) = 2x, F(1) = 3. Найдите F(x).", "solution": "F(x) = x² + C. F(1) = 1+C = 3 → C = 2. F(x) = x² + 2.", "difficulty_level": 1}]},
        ]}],
    )

    # 7. Определённый интеграл
    ops += _build_ops_from_topic_def(
        "TOP-OPREDELYONNYJ-INTEGRAL-2f73d5", "SKL-OPRED-INTEGR-SEED", "Определённый интеграл",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-OPREDINT-NEWTON", "title": "Формула Ньютона—Лейбница",
             "description": "∫[a;b] f(x)dx = F(b) − F(a). Геометрический смысл: площадь криволинейной трапеции (со знаком). Колмогоров А.Н. 10-11 кл., §12.",
             "examples": [{"uid": "EX-OPREDINT-NEW-1", "title": "Ньютон—Лейбниц", "statement": "∫₀² (3x²)dx.", "solution": "F(x) = x³. F(2)−F(0) = 8−0 = 8.", "difficulty_level": 1}]},
            {"uid": "MET-OPREDINT-PLOSHCHAD", "title": "Площадь фигуры",
             "description": "S = ∫[a;b] |f(x)|dx. Между двумя кривыми: S = ∫[a;b] |f(x)−g(x)|dx. Колмогоров А.Н. 10-11 кл., §12.",
             "examples": [{"uid": "EX-OPREDINT-PLOSH-1", "title": "Площадь между кривыми", "statement": "Площадь между y=x² и y=x на [0;1].", "solution": "S = ∫₀¹ (x−x²)dx = [x²/2 − x³/3]₀¹ = 1/2 − 1/3 = 1/6.", "difficulty_level": 2}]},
            {"uid": "MET-OPREDINT-SVOJSTVA", "title": "Свойства определённого интеграла",
             "description": "Линейность: ∫(af+bg) = a∫f + b∫g. Аддитивность: ∫[a;c] = ∫[a;b] + ∫[b;c]. Оценка: m(b−a) ≤ ∫ ≤ M(b−a). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-OPREDINT-SV-1", "title": "Свойства", "statement": "Оцените ∫₀¹ eˣ dx.", "solution": "На [0;1]: e⁰ ≤ eˣ ≤ e¹. 1·1 ≤ ∫ ≤ e·1. 1 ≤ ∫ ≤ e ≈ 2.718. Точно: e−1 ≈ 1.718.", "difficulty_level": 2}]},
        ]}],
    )

    # 8. Применения интеграла
    ops += _build_ops_from_topic_def(
        "TOP-PRIMENENIYA-INTEGRALA-d4e675", "SKL-PRIMEN-INTEGR-SEED", "Применения интеграла",
        [{"uc_min": 10, "uc_max": 11, "methods": [
            {"uid": "MET-PRIMINT-OBJEM", "title": "Объём тела вращения",
             "description": "V = π∫[a;b] f²(x)dx (вращение вокруг Ox). V = π∫[c;d] g²(y)dy (вокруг Oy). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PRIMINT-OBJ-1", "title": "Тело вращения", "statement": "Объём при вращении y=x² вокруг Ox на [0;2].", "solution": "V = π∫₀² x⁴dx = π·x⁵/5|₀² = π·32/5 = 32π/5.", "difficulty_level": 2}]},
            {"uid": "MET-PRIMINT-DLINA", "title": "Длина кривой",
             "description": "L = ∫[a;b] √(1+(f'(x))²) dx. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PRIMINT-DLINA-1", "title": "Длина кривой", "statement": "Длина y=x^(3/2) на [0;4].", "solution": "f'=3√x/2. L = ∫₀⁴ √(1+9x/4)dx. u=1+9x/4. L = (8/27)(10√10−1) ≈ 9.07.", "difficulty_level": 3}]},
            {"uid": "MET-PRIMINT-FIZIKA", "title": "Физические приложения",
             "description": "Путь: s = ∫v(t)dt. Работа: A = ∫F(x)dx. Масса: m = ∫ρ(x)dx. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PRIMINT-FIZ-1", "title": "Путь за время", "statement": "v(t) = 3t² м/с. Путь за 0 ≤ t ≤ 2.", "solution": "s = ∫₀² 3t²dt = t³|₀² = 8 м.", "difficulty_level": 1}]},
        ]}],
    )

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Математические основания  (10 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _foundations_ops() -> list[dict]:
    ops: list[dict] = []

    # 1. Понятие множества (7-8)
    ops += _build_ops_from_topic_def(
        "TOP-PONYATIE-MNOZHESTVA-124deb", "SKL-PONYATIE-MNOZH-SEED", "Понятие множества",
        [{"uc_min": 7, "uc_max": 8, "methods": [
            {"uid": "MET-MNOZH-SPOSOBY", "title": "Способы задания множества",
             "description": "Перечислением: A = {1,2,3}. Свойством: B = {x | x > 0}. Диаграммы Эйлера-Венна. Пустое множество ∅. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-MNOZH-SPOS-1", "title": "Задание множества", "statement": "Запишите множество чётных чисел от 2 до 10.", "solution": "A = {2, 4, 6, 8, 10} или A = {x ∈ ℕ | 2 ≤ x ≤ 10, x — чётное}.", "difficulty_level": 1}]},
            {"uid": "MET-MNOZH-PODMNOZH", "title": "Подмножество и принадлежность",
             "description": "a ∈ A — элемент принадлежит. A ⊆ B — A подмножество B (каждый элемент A есть в B). |A| — мощность (число элементов). Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-MNOZH-PODMN-1", "title": "Подмножество", "statement": "A = {1,2,3}, B = {1,2,3,4,5}. A ⊆ B?", "solution": "Да, каждый элемент A (1,2,3) содержится в B.", "difficulty_level": 1}]},
            {"uid": "MET-MNOZH-CHISLOVYE", "title": "Числовые множества",
             "description": "ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ. ℕ — натуральные. ℤ — целые. ℚ — рациональные. ℝ — действительные. ℝ\\ℚ — иррациональные. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-MNOZH-CHISL-1", "title": "Классификация чисел", "statement": "К каким множествам принадлежит √4? А √3?", "solution": "√4 = 2 ∈ ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ. √3 ∈ ℝ\\ℚ (иррациональное).", "difficulty_level": 1}]},
        ]}],
    )

    # 2. Операции над множествами (7-8)
    ops += _build_ops_from_topic_def(
        "TOP-OPERATSII-NAD-MNOZHESTVAMI-0c2eef", "SKL-OPER-MNOZH-SEED", "Операции над множествами",
        [{"uc_min": 7, "uc_max": 8, "methods": [
            {"uid": "MET-OPMN-OBEDPERES", "title": "Объединение и пересечение",
             "description": "A ∪ B — все элементы A и B. A ∩ B — общие элементы. A \\ B — элементы A, не входящие в B. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-OPMN-OBED-1", "title": "Объединение и пересечение", "statement": "A={1,2,3,4}, B={3,4,5,6}. A∪B? A∩B?", "solution": "A∪B = {1,2,3,4,5,6}. A∩B = {3,4}.", "difficulty_level": 1}]},
            {"uid": "MET-OPMN-DOPOLNENIE", "title": "Дополнение и разность",
             "description": "Ā = U \\ A (дополнение в универсуме U). A \\ B — элементы A, не входящие в B. A △ B = (A\\B)∪(B\\A) — симметрическая разность. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-OPMN-DOPOL-1", "title": "Разность множеств", "statement": "A={1,2,3,4,5}, B={2,4,6}. A\\B?", "solution": "A\\B = {1,3,5} (убираем общие с B).", "difficulty_level": 1}]},
            {"uid": "MET-OPMN-FORMULA-VKL", "title": "Формула включений-исключений",
             "description": "|A∪B| = |A| + |B| − |A∩B|. Для трёх: |A∪B∪C| = |A|+|B|+|C| − |A∩B|−|A∩C|−|B∩C| + |A∩B∩C|. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-OPMN-VKL-1", "title": "Включения-исключения", "statement": "В классе 30 учеников, 20 любят математику, 18 физику, 12 — оба предмета. Сколько любят хотя бы один?", "solution": "|M∪Ф| = 20 + 18 − 12 = 26.", "difficulty_level": 1}]},
        ]}],
    )

    # 3-5: Высказывания, Логические связки, Логические законы (7-9)
    for uid, skl_uid, title, uc_min, uc_max, methods in [
        ("TOP-VYSKAZYVANIYA-efcd74", "SKL-VYSKAZ-SEED", "Высказывания", 7, 8, [
            {"uid": "MET-VYSK-ISTLOZH", "title": "Истинные и ложные высказывания",
             "description": "Высказывание — утверждение, которое либо истинно (И), либо ложно (Л). «2+2=4» — И. «5>7» — Л. Вопросы и команды — не высказывания. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-VYSK-ISTL-1", "title": "Определение истинности", "statement": "Определите: «Москва — столица России», «3 > 10», «Закройте дверь».", "solution": "И, Л, не является высказыванием.", "difficulty_level": 1}]},
            {"uid": "MET-VYSK-OTRITSANIE", "title": "Отрицание высказывания",
             "description": "¬A — истинно, когда A ложно, и наоборот. Отрицание «все» → «существует, что нет». Отрицание «существует» → «для всех нет». Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-VYSK-OTR-1", "title": "Отрицание", "statement": "Постройте отрицание: «Все числа положительны».", "solution": "«Существует число, которое не положительно» (т.е. ≤ 0).", "difficulty_level": 1}]},
            {"uid": "MET-VYSK-USLOVNYE", "title": "Условные высказывания",
             "description": "«Если A, то B» (импликация A → B). Ложна только когда A истинно, а B ложно. Обратное: B → A. Противоположное: ¬A → ¬B. Контрапозиция: ¬B → ¬A (эквивалентна A→B). Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-VYSK-USLOV-1", "title": "Импликация", "statement": "«Если n делится на 6, то n делится на 3». Истинно? Верно ли обратное?", "solution": "Истинно (6=2·3). Обратное «если на 3, то на 6» — ложно (9 делится на 3, но не на 6).", "difficulty_level": 1}]},
        ]),
        ("TOP-LOGICHESKIE-SVYAZKI-9db1f9", "SKL-LOG-SVYAZKI-SEED", "Логические связки", 8, 9, [
            {"uid": "MET-LOGSV-KONJDISJ", "title": "Конъюнкция и дизъюнкция",
             "description": "A ∧ B (И): истинно, если оба истинны. A ∨ B (ИЛИ): ложно, если оба ложны. Приоритет: ¬ > ∧ > ∨. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-LOGSV-KD-1", "title": "Конъюнкция и дизъюнкция", "statement": "A = И, B = Л. Найдите A∧B и A∨B.", "solution": "A∧B = Л (не оба истинны). A∨B = И (хотя бы одно истинно).", "difficulty_level": 1}]},
            {"uid": "MET-LOGSV-IMPLIK", "title": "Импликация и эквивалентность",
             "description": "A → B (если A, то B): ложна только при A=И, B=Л. A ↔ B (тогда и только тогда): истинна при одинаковых значениях. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-LOGSV-IMPL-1", "title": "Таблица импликации", "statement": "Составьте таблицу истинности A → B.", "solution": "И→И=И, И→Л=Л, Л→И=И, Л→Л=И.", "difficulty_level": 1}]},
            {"uid": "MET-LOGSV-FORMULY", "title": "Построение формул",
             "description": "Запись составных высказываний формулами: «x > 0 и x < 5» → (x>0) ∧ (x<5). Порядок операций: скобки, ¬, ∧, ∨, →, ↔. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-LOGSV-FORM-1", "title": "Формализация", "statement": "Запишите формулой: «x чётное или x > 10, но не оба».", "solution": "(A ∨ B) ∧ ¬(A ∧ B), где A = «x чётное», B = «x > 10». Это A ⊕ B (XOR).", "difficulty_level": 2}]},
        ]),
        ("TOP-LOGICHESKIE-ZAKONY-3b4f49", "SKL-LOG-ZAKONY-SEED", "Логические законы", 8, 9, [
            {"uid": "MET-LOGZAK-DE-MORGAN", "title": "Законы де Моргана",
             "description": "¬(A∧B) = ¬A ∨ ¬B. ¬(A∨B) = ¬A ∧ ¬B. Позволяют раскрывать отрицание над сложными высказываниями. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-LOGZAK-DEM-1", "title": "Де Морган", "statement": "Упростите: ¬(x>0 ∧ x<5).", "solution": "x ≤ 0 ∨ x ≥ 5 (по закону де Моргана).", "difficulty_level": 1}]},
            {"uid": "MET-LOGZAK-RASPRED", "title": "Распределительные и идемпотентные законы",
             "description": "A∧(B∨C) = (A∧B)∨(A∧C). A∨(B∧C) = (A∨B)∧(A∨C). A∧A = A. A∨A = A. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-LOGZAK-RASP-1", "title": "Распределительный закон", "statement": "Упростите: (A∧B) ∨ (A∧C).", "solution": "A ∧ (B ∨ C).", "difficulty_level": 1}]},
            {"uid": "MET-LOGZAK-TAVTOLOG", "title": "Тавтологии и противоречия",
             "description": "Тавтология — формула, всегда истинная (A∨¬A). Противоречие — всегда ложная (A∧¬A). Если F — тавтология, ¬F — противоречие. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-LOGZAK-TAVT-1", "title": "Тавтология", "statement": "Является ли (A→B)↔(¬A∨B) тавтологией?", "solution": "Да. Проверка таблицей: И→И=И, ¬И∨И=И; И→Л=Л, ¬И∨Л=Л; ... Совпадают во всех строках.", "difficulty_level": 2}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": uc_min, "uc_max": uc_max, "methods": methods}])

    # 6-10: Кванторы, Методы доказательства, Отношения, Отображения, Эквивалентность (10-11)
    for uid, skl_uid, title, methods in [
        ("TOP-KVANTORY-830065", "SKL-KVANTORY-SEED", "Кванторы", [
            {"uid": "MET-KVANT-VSUSH", "title": "Кванторы всеобщности и существования",
             "description": "∀x P(x) — «для всех x верно P(x)». ∃x P(x) — «существует x, для которого P(x)». Отрицание: ¬∀x P(x) = ∃x ¬P(x). Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-KVANT-VSUSH-1", "title": "Запись с кванторами", "statement": "Запишите: «для любого x существует y такой что x+y=0».", "solution": "∀x ∃y (x + y = 0). (y = −x.)", "difficulty_level": 2}]},
            {"uid": "MET-KVANT-OTRIT", "title": "Отрицание кванторных формул",
             "description": "¬∀x∃y P(x,y) = ∃x∀y ¬P(x,y). Каждый ∀ меняется на ∃ и наоборот, P → ¬P. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-KVANT-OTR-1", "title": "Отрицание", "statement": "Отрицание: ∃x∀y (x·y = y).", "solution": "∀x∃y (x·y ≠ y). «Для любого x существует y, для которого x·y ≠ y».", "difficulty_level": 2}]},
            {"uid": "MET-KVANT-OGRANICH", "title": "Ограниченные кванторы",
             "description": "∀x∈A P(x) — для всех x из A. ∃x∈A P(x) — существует x в A. Позволяют уточнять область действия. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-KVANT-OGR-1", "title": "Ограниченный квантор", "statement": "∀n∈ℕ (n² ≥ n). Верно?", "solution": "Да. При n ≥ 1: n² = n·n ≥ n·1 = n.", "difficulty_level": 2}]},
        ]),
        ("TOP-METODY-DOKAZATELSTVA-c72a13", "SKL-METODY-DOKAZ-SEED", "Методы доказательства", [
            {"uid": "MET-DOKAZ-PRYAMOE", "title": "Прямое доказательство",
             "description": "Цепочка логических следствий от условий к заключению. A₁ → A₂ → ... → B. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-DOKAZ-PRYAM-1", "title": "Прямое доказательство", "statement": "Докажите: сумма двух чётных чисел чётна.", "solution": "Пусть a=2m, b=2n. a+b = 2m+2n = 2(m+n) — чётное. ЧТД.", "difficulty_level": 1}]},
            {"uid": "MET-DOKAZ-OT-PROTIVNOGO", "title": "Доказательство от противного",
             "description": "Предполагаем ¬B и приходим к противоречию. Значит B истинно. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-DOKAZ-PROT-1", "title": "От противного", "statement": "Докажите: √2 иррационально.", "solution": "Предположим √2 = p/q (несократимая). 2 = p²/q². p² = 2q² → p чётное, p=2k. 4k² = 2q² → q² = 2k² → q чётное. Противоречие (дробь несократимая). ЧТД.", "difficulty_level": 3}]},
            {"uid": "MET-DOKAZ-INDUKTSIYA", "title": "Математическая индукция",
             "description": "1) База: проверяем для n=1. 2) Шаг: предполагаем для n=k, доказываем для n=k+1. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-DOKAZ-IND-1", "title": "Индукция", "statement": "Докажите: 1+2+...+n = n(n+1)/2.", "solution": "База: n=1: 1 = 1·2/2 ✓. Шаг: S(k+1) = S(k)+(k+1) = k(k+1)/2+(k+1) = (k+1)(k+2)/2 ✓.", "difficulty_level": 2}]},
        ]),
        ("TOP-OTNOSHENIYA-142ca8", "SKL-OTNOSH-SEED", "Отношения", [
            {"uid": "MET-OTNO-SVOJSTVA", "title": "Свойства отношений",
             "description": "Рефлексивность: aRa. Симметричность: aRb → bRa. Транзитивность: aRb ∧ bRc → aRc. Антисимметричность: aRb ∧ bRa → a=b. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OTNO-SV-1", "title": "Свойства ≤", "statement": "Какие свойства у отношения ≤ на ℤ?", "solution": "Рефлексивно (a≤a). Антисимметрично (a≤b, b≤a → a=b). Транзитивно (a≤b, b≤c → a≤c). Не симметрично.", "difficulty_level": 2}]},
            {"uid": "MET-OTNO-EKVIVALENT", "title": "Отношение эквивалентности",
             "description": "Рефлексивное + симметричное + транзитивное. Разбивает множество на классы эквивалентности. Пример: равенство остатков при делении. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OTNO-EKV-1", "title": "Классы эквивалентности", "statement": "Отношение на ℤ: a~b ⟺ a−b делится на 3. Классы?", "solution": "[0] = {0,3,6,...}, [1] = {1,4,7,...}, [2] = {2,5,8,...}. Три класса: остатки 0, 1, 2.", "difficulty_level": 2}]},
            {"uid": "MET-OTNO-PORYADOK", "title": "Отношение порядка",
             "description": "Рефлексивное + антисимметричное + транзитивное → частичный порядок. Если любые два сравнимы → линейный порядок. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OTNO-POR-1", "title": "Частичный порядок", "statement": "Делимость на ℕ — порядок?", "solution": "a|a (рефл.), a|b∧b|a→a=b (антисимм.), a|b∧b|c→a|c (транз.). Да, частичный (не все сравнимы: 2 и 3).", "difficulty_level": 2}]},
        ]),
        ("TOP-OTOBRAZHENIYA-eb11ba", "SKL-OTOBR-SEED", "Отображения", [
            {"uid": "MET-OTOBR-VIDY", "title": "Инъекция, сюръекция, биекция",
             "description": "Инъекция: f(a)=f(b)→a=b. Сюръекция: для любого y существует x: f(x)=y. Биекция: и то, и другое. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OTOBR-VID-1", "title": "Виды отображений", "statement": "f: ℝ→ℝ, f(x)=x². Инъекция? Сюръекция?", "solution": "Не инъекция: f(2)=f(−2)=4. Не сюръекция: −1 не имеет прообраза. Если f: ℝ₊→ℝ₊ — биекция.", "difficulty_level": 2}]},
            {"uid": "MET-OTOBR-KOMPOZIT", "title": "Композиция отображений",
             "description": "(g∘f)(x) = g(f(x)). Сначала f, потом g. Ассоциативна: (h∘g)∘f = h∘(g∘f). Не коммутативна. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OTOBR-KOMP-1", "title": "Композиция", "statement": "f(x)=2x+1, g(x)=x². Найдите (g∘f)(3) и (f∘g)(3).", "solution": "g(f(3)) = g(7) = 49. f(g(3)) = f(9) = 19. Не равны.", "difficulty_level": 2}]},
            {"uid": "MET-OTOBR-OBRATNOE", "title": "Обратное отображение",
             "description": "f⁻¹ существует ⟺ f — биекция. f⁻¹(f(x))=x и f(f⁻¹(y))=y. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OTOBR-OBR-1", "title": "Обратное отображение", "statement": "f(x)=3x−6. Найдите f⁻¹.", "solution": "y=3x−6 → x=(y+6)/3. f⁻¹(x)=(x+6)/3.", "difficulty_level": 1}]},
        ]),
        ("TOP-EKVIVALENTNOST-I-PORYADOK-a24b0a", "SKL-EKVIV-PORYAD-SEED", "Эквивалентность и порядок", [
            {"uid": "MET-EKVPOR-KLASSY", "title": "Классы эквивалентности и фактор-множество",
             "description": "Класс [a] = {x | x~a}. Фактор-множество A/~ = {[a] | a∈A}. Классы не пересекаются и покрывают всё A. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-EKVPOR-KL-1", "title": "Фактор-множество", "statement": "ℤ/~, где a~b ⟺ 2|(a−b). Опишите фактор-множество.", "solution": "Два класса: чётные [0]={0,±2,±4,...} и нечётные [1]={±1,±3,...}. ℤ/~ = {[0], [1]}.", "difficulty_level": 2}]},
            {"uid": "MET-EKVPOR-DIAGRAMMA", "title": "Диаграмма Хассе",
             "description": "Графическое представление частичного порядка. Элементы — вершины, стрелки — порядок (снизу вверх). Транзитивные связи опускаются. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-EKVPOR-HASSE-1", "title": "Диаграмма Хассе", "statement": "Делители 12: {1,2,3,4,6,12}. Постройте диаграмму по делимости.", "solution": "1→2→4→12, 1→3→6→12, 2→6. (1 внизу, 12 вверху.)", "difficulty_level": 2}]},
            {"uid": "MET-EKVPOR-RESHYOTKA", "title": "Решётка",
             "description": "Частично упорядоченное множество, где любые два элемента имеют sup (∨) и inf (∧). Пример: делители числа по делимости. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-EKVPOR-RESH-1", "title": "Решётка", "statement": "Делители 30. Найдите 6∨10 и 6∧10.", "solution": "6∨10 = НОК(6,10) = 30. 6∧10 = НОД(6,10) = 2.", "difficulty_level": 2}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 10, "uc_max": 11, "methods": methods}])

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Линейная алгебра  (6 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _linear_algebra_ops() -> list[dict]:
    ops: list[dict] = []

    for uid, skl_uid, title, methods in [
        ("TOP-MATRITSY-c1cc7f", "SKL-MATRITSY-SEED", "Матрицы", [
            {"uid": "MET-MATR-OPERATSII", "title": "Операции с матрицами",
             "description": "Сложение: поэлементно (размеры совпадают). Умножение на число: каждый элемент. Умножение: (AB)ᵢⱼ = Σ aᵢₖbₖⱼ. Размеры: (m×n)(n×p) = (m×p). AB ≠ BA. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-MATR-OPER-1", "title": "Умножение матриц", "statement": "A=[[1,2],[3,4]], B=[[5,6],[7,8]]. AB=?", "solution": "AB = [[1·5+2·7, 1·6+2·8],[3·5+4·7, 3·6+4·8]] = [[19,22],[43,50]].", "difficulty_level": 2}]},
            {"uid": "MET-MATR-TRANSPON", "title": "Транспонирование",
             "description": "(Aᵀ)ᵢⱼ = Aⱼᵢ. Свойства: (AB)ᵀ = BᵀAᵀ. (A+B)ᵀ = Aᵀ+Bᵀ. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-MATR-TRANSP-1", "title": "Транспонирование", "statement": "A=[[1,2,3],[4,5,6]]. Aᵀ=?", "solution": "Aᵀ = [[1,4],[2,5],[3,6]].", "difficulty_level": 1}]},
            {"uid": "MET-MATR-EDINNUL", "title": "Единичная и нулевая матрицы",
             "description": "E (единичная): eᵢᵢ=1, остальные 0. AE = EA = A. O (нулевая): все 0. A+O = A. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-MATR-EDIN-1", "title": "Единичная матрица", "statement": "A=[[3,1],[2,4]]. Проверьте AE=A.", "solution": "AE = [[3·1+1·0, 3·0+1·1],[2·1+4·0, 2·0+4·1]] = [[3,1],[2,4]] = A ✓.", "difficulty_level": 1}]},
        ]),
        ("TOP-OPREDELITELI-3723cc", "SKL-OPREDEL-SEED", "Определители", [
            {"uid": "MET-OPRED-2x2", "title": "Определитель 2×2",
             "description": "det[[a,b],[c,d]] = ad − bc. Свойства: det(AB) = det A · det B. det(kA) = k²·det A. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OPRED-2X2-1", "title": "Определитель 2×2", "statement": "det[[3,2],[1,4]] = ?", "solution": "3·4 − 2·1 = 12 − 2 = 10.", "difficulty_level": 1}]},
            {"uid": "MET-OPRED-3x3", "title": "Определитель 3×3 (правило Саррюса)",
             "description": "Дописываем 1-й и 2-й столбцы. Произведения по главным диагоналям (+) минус побочным (−). Или разложение по строке/столбцу. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OPRED-3X3-1", "title": "Определитель 3×3", "statement": "det[[1,2,3],[4,5,6],[7,8,9]] = ?", "solution": "= 1·5·9+2·6·7+3·4·8 − 3·5·7−2·4·9−1·6·8 = 45+84+96−105−72−48 = 0.", "difficulty_level": 2}]},
            {"uid": "MET-OPRED-SVOJSTVA", "title": "Свойства определителей",
             "description": "При перестановке строк — смена знака. При пропорциональных строках det=0. Прибавление кратной строки не меняет det. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OPRED-SV-1", "title": "Свойство нулевого определителя", "statement": "Почему det=0 в предыдущем примере?", "solution": "3-я строка = 2·(2-я строка) − (1-я строка): 7=2·4−1, 8=2·5−2, 9=2·6−3. Линейная зависимость → det=0.", "difficulty_level": 2}]},
        ]),
        ("TOP-OBRATNAYA-MATRITSA-c589a4", "SKL-OBRATN-MATR-SEED", "Обратная матрица", [
            {"uid": "MET-OBRMATR-FORMULA", "title": "Обратная матрица 2×2",
             "description": "A⁻¹ = (1/det A)·[[d,−b],[−c,a]] для A=[[a,b],[c,d]]. Существует ⟺ det A ≠ 0. AA⁻¹ = E. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OBRMATR-FORM-1", "title": "Обратная 2×2", "statement": "A=[[2,1],[5,3]]. A⁻¹=?", "solution": "det A = 6−5 = 1. A⁻¹ = [[3,−1],[−5,2]]. Проверка: AA⁻¹ = E ✓.", "difficulty_level": 2}]},
            {"uid": "MET-OBRMATR-GAUSS", "title": "Нахождение A⁻¹ методом Гаусса",
             "description": "Составляем [A|E] и элементарными преобразованиями приводим к [E|A⁻¹]. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OBRMATR-GAUSS-1", "title": "Метод Гаусса", "statement": "A=[[1,2],[3,7]]. Найдите A⁻¹ методом Гаусса.", "solution": "[1 2|1 0; 3 7|0 1] → R₂−3R₁ → [1 2|1 0; 0 1|−3 1] → R₁−2R₂ → [1 0|7 −2; 0 1|−3 1]. A⁻¹=[[7,−2],[−3,1]].", "difficulty_level": 2}]},
            {"uid": "MET-OBRMATR-RESHENIE", "title": "Решение систем через обратную матрицу",
             "description": "AX = B ⟹ X = A⁻¹B. Применимо, если det A ≠ 0. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-OBRMATR-RESH-1", "title": "Матричное решение", "statement": "{2x+y=5, 5x+3y=13}. Решите через A⁻¹.", "solution": "A=[[2,1],[5,3]], B=[5,13]ᵀ. A⁻¹=[[3,−1],[−5,2]]. X=A⁻¹B=[15−13,−25+26]ᵀ=[2,1]ᵀ. x=2, y=1.", "difficulty_level": 2}]},
        ]),
        ("TOP-LINEJNAYA-KOMBINATSIYA-31422b", "SKL-LIN-KOMB-SEED", "Линейная комбинация", [
            {"uid": "MET-LINKOMB-OPRED", "title": "Линейная комбинация и линейная зависимость",
             "description": "Линейная комбинация: α₁v₁+α₂v₂+...+αₙvₙ. Линейно зависимы, если существуют не все нулевые коэффициенты, дающие 0. Иначе — независимы. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-LINKOMB-OPR-1", "title": "Линейная зависимость", "statement": "v₁=(1,2), v₂=(2,4). Зависимы?", "solution": "v₂ = 2v₁. Зависимы: 2v₁ − v₂ = 0.", "difficulty_level": 1}]},
            {"uid": "MET-LINKOMB-RANG", "title": "Ранг системы векторов",
             "description": "Максимальное число линейно независимых векторов. Ранг матрицы = ранг столбцов = ранг строк. Находится приведением к ступенчатому виду. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-LINKOMB-RANG-1", "title": "Ранг матрицы", "statement": "A=[[1,2,3],[2,4,6],[1,3,5]]. Ранг?", "solution": "R₂−2R₁, R₃−R₁: [[1,2,3],[0,0,0],[0,1,2]]. Переставим: [[1,2,3],[0,1,2],[0,0,0]]. Ранг = 2.", "difficulty_level": 2}]},
            {"uid": "MET-LINKOMB-OBOLOCHKA", "title": "Линейная оболочка",
             "description": "span(v₁,...,vₖ) — множество всех линейных комбинаций. Если span = ℝⁿ, то v₁,...,vₖ порождают ℝⁿ. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-LINKOMB-OBOL-1", "title": "Линейная оболочка", "statement": "v₁=(1,0), v₂=(0,1). span(v₁,v₂)?", "solution": "α(1,0)+β(0,1) = (α,β) — любой вектор ℝ². span = ℝ².", "difficulty_level": 1}]},
        ]),
        ("TOP-BAZIS-9efbe8", "SKL-BAZIS-SEED", "Базис", [
            {"uid": "MET-BAZIS-OPRED", "title": "Определение базиса",
             "description": "Базис пространства V — линейно независимая система, порождающая V. В ℝⁿ базис содержит ровно n векторов. Стандартный базис: e₁=(1,0,...), e₂=(0,1,...), ... Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-BAZIS-OPR-1", "title": "Является ли базисом?", "statement": "v₁=(1,1), v₂=(1,−1) — базис ℝ²?", "solution": "det[[1,1],[1,−1]] = −2 ≠ 0 → линейно независимы. 2 вектора в ℝ² → базис.", "difficulty_level": 2}]},
            {"uid": "MET-BAZIS-KOORDINATY", "title": "Координаты вектора в базисе",
             "description": "v = α₁e₁ + α₂e₂ + ... + αₙeₙ. Координаты (α₁,...,αₙ) единственны. Для нахождения: решаем систему. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-BAZIS-KOORD-1", "title": "Координаты в базисе", "statement": "Базис: v₁=(1,1), v₂=(1,−1). Найдите координаты w=(3,1) в этом базисе.", "solution": "α₁+α₂=3, α₁−α₂=1. α₁=2, α₂=1. w = 2v₁ + 1v₂.", "difficulty_level": 2}]},
            {"uid": "MET-BAZIS-PEREHOD", "title": "Матрица перехода между базисами",
             "description": "Если новый базис {f₁,...,fₙ} выражен через старый {e₁,...,eₙ}: fⱼ = Σ pᵢⱼeᵢ, то P — матрица перехода. Новые координаты: x' = P⁻¹x. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-BAZIS-PEREH-1", "title": "Матрица перехода", "statement": "Старый базис: e₁,e₂. Новый: f₁=e₁+e₂, f₂=e₁−e₂. Матрица перехода?", "solution": "P = [[1,1],[1,−1]]. Координаты в новом: x'=P⁻¹x.", "difficulty_level": 2}]},
        ]),
        ("TOP-RAZMERNOST-cb7976", "SKL-RAZMERN-SEED", "Размерность", [
            {"uid": "MET-RAZM-OPRED", "title": "Размерность линейного пространства",
             "description": "dim V = число векторов в базисе. dim ℝⁿ = n. dim {0} = 0. Размерность подпространства ≤ dim V. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-RAZM-OPR-1", "title": "Размерность подпространства", "statement": "W = {(x,y,z) | x+y+z=0} ⊂ ℝ³. dim W?", "solution": "z = −x−y. Базис: (1,0,−1), (0,1,−1). dim W = 2.", "difficulty_level": 2}]},
            {"uid": "MET-RAZM-FORMULA", "title": "Формула размерности суммы",
             "description": "dim(U+W) = dim U + dim W − dim(U∩W). Прямая сумма: U⊕W ⟺ U∩W = {0}. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-RAZM-FORM-1", "title": "Размерность суммы", "statement": "dim U=3, dim W=2, dim(U∩W)=1. dim(U+W)?", "solution": "dim(U+W) = 3+2−1 = 4.", "difficulty_level": 2}]},
            {"uid": "MET-RAZM-RANG-NULLNOST", "title": "Теорема о ранге и нульности",
             "description": "Для линейного отображения f: V→W: dim V = dim(ker f) + dim(Im f). rank(A) + nullity(A) = n. Алимов Ш.А. 10-11 кл.",
             "examples": [{"uid": "EX-RAZM-RANGNUL-1", "title": "Ранг и нульность", "statement": "A — матрица 3×4, rank A = 2. Найдите размерность ядра.", "solution": "nullity = 4 − 2 = 2.", "difficulty_level": 2}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 10, "uc_max": 11, "methods": methods}])

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Дискретная математика  (6 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _discrete_math_ops() -> list[dict]:
    ops: list[dict] = []

    # 8-9 кл topics
    for uid, skl_uid, title, uc_min, uc_max, methods in [
        ("TOP-GRAFY-21142f", "SKL-GRAFY-SEED", "Графы", 8, 9, [
            {"uid": "MET-GRAF-OPRED", "title": "Основные понятия теории графов",
             "description": "Граф G=(V,E): вершины V и рёбра E. Степень вершины deg(v) — число инцидентных рёбер. Сумма степеней = 2|E| (лемма о рукопожатиях). Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-GRAF-OPR-1", "title": "Степени вершин", "statement": "5 вершин, степени 2,3,3,2,2. Сколько рёбер?", "solution": "Σ deg = 2+3+3+2+2 = 12. |E| = 12/2 = 6.", "difficulty_level": 1}]},
            {"uid": "MET-GRAF-EILER-GAMILT", "title": "Эйлеровы и гамильтоновы графы",
             "description": "Эйлеров путь (все рёбра): существует ⟺ ≤2 вершин нечётной степени. Гамильтонов цикл (все вершины): NP-полная задача. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-GRAF-EILER-1", "title": "Эйлеров путь", "statement": "Граф Кёнигсбергских мостов: 4 вершины со степенями 3,3,3,5. Есть ли Эйлеров путь?", "solution": "4 вершины нечётной степени (>2). Эйлерова пути нет.", "difficulty_level": 1}]},
            {"uid": "MET-GRAF-SVYAZNOST", "title": "Связность графа",
             "description": "Связный: между любыми двумя вершинами есть путь. Компонента связности — максимальный связный подграф. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-GRAF-SVYAZ-1", "title": "Компоненты связности", "statement": "6 вершин, рёбра: (1,2),(2,3),(4,5). Сколько компонент?", "solution": "3 компоненты: {1,2,3}, {4,5}, {6}.", "difficulty_level": 1}]},
        ]),
        ("TOP-DEREVYA-6faba1", "SKL-DEREVYA-SEED", "Деревья", 8, 9, [
            {"uid": "MET-DEREV-OPRED", "title": "Дерево как связный граф без циклов",
             "description": "Дерево: связный ациклический граф. |E| = |V|−1. Между любыми двумя вершинами единственный путь. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-DEREV-OPR-1", "title": "Свойства дерева", "statement": "Дерево с 10 вершинами. Сколько рёбер?", "solution": "|E| = 10 − 1 = 9.", "difficulty_level": 1}]},
            {"uid": "MET-DEREV-OBHOD", "title": "Обход дерева",
             "description": "Прямой (pre-order): корень→левый→правый. Симметричный (in-order): левый→корень→правый. Обратный (post-order): левый→правый→корень. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-DEREV-OBHOD-1", "title": "Обход двоичного дерева", "statement": "Корень A, левый B(лев D, пр E), правый C. In-order?", "solution": "D, B, E, A, C.", "difficulty_level": 1}]},
            {"uid": "MET-DEREV-OSTOV", "title": "Остовное дерево",
             "description": "Остовное дерево — подграф, содержащий все вершины и являющийся деревом. Минимальное остовное — с наименьшей суммой весов рёбер (Краскал, Прим). Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-DEREV-OSTOV-1", "title": "Число рёбер остовного дерева", "statement": "Граф из 7 вершин. Сколько рёбер в остовном дереве?", "solution": "7 − 1 = 6 рёбер.", "difficulty_level": 1}]},
        ]),
        ("TOP-TABLITSY-ISTINNOSTI-e872d3", "SKL-TABL-ISTIN-SEED", "Таблицы истинности", 8, 9, [
            {"uid": "MET-TABLIST-POSTROENIE", "title": "Построение таблицы истинности",
             "description": "Для n переменных — 2ⁿ строк. Столбцы: переменные, промежуточные вычисления, итоговая формула. Вычисляем по приоритету: ¬, ∧, ∨, →, ↔. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-TABLIST-POST-1", "title": "Таблица истинности", "statement": "Постройте таблицу: A ∧ (B ∨ ¬A).", "solution": "A=0,B=0: 0∧(0∨1)=0. A=0,B=1: 0∧(1∨1)=0. A=1,B=0: 1∧(0∨0)=0. A=1,B=1: 1∧(1∨0)=1.", "difficulty_level": 1}]},
            {"uid": "MET-TABLIST-EKVIV", "title": "Проверка эквивалентности формул",
             "description": "Две формулы эквивалентны, если их таблицы истинности совпадают. A→B ≡ ¬A∨B. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-TABLIST-EKV-1", "title": "Эквивалентность", "statement": "Эквивалентны ли ¬(A∧B) и ¬A∨¬B?", "solution": "По закону де Моргана — да. Проверка таблицей: все 4 строки совпадают.", "difficulty_level": 1}]},
            {"uid": "MET-TABLIST-DNF-KNF", "title": "ДНФ и КНФ",
             "description": "ДНФ: дизъюнкция конъюнкций. КНФ: конъюнкция дизъюнкций. СДНФ строится по единицам таблицы. СКНФ — по нулям. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-TABLIST-DNF-1", "title": "СДНФ", "statement": "f(A,B) = 1 при (0,1) и (1,1). СДНФ?", "solution": "f = (¬A∧B) ∨ (A∧B) = B.", "difficulty_level": 2}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": uc_min, "uc_max": uc_max, "methods": methods}])

    # 9-11 кл topics
    for uid, skl_uid, title, methods in [
        ("TOP-PUTI-I-TSIKLY-17a10d", "SKL-PUTI-TSIKLY-SEED", "Пути и циклы", [
            {"uid": "MET-PUTICIK-DIJKSTRA", "title": "Кратчайший путь (алгоритм Дейкстры)",
             "description": "Для взвешенного графа с неотрицательными весами. Последовательно выбираем ближайшую непосещённую вершину. Сложность O(V²). Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-PUTICIK-DIJK-1", "title": "Кратчайший путь", "statement": "A→B:4, A→C:1, C→B:2. Кратчайший A→B?", "solution": "Через C: 1+2 = 3 < 4. Кратчайший: A→C→B, длина 3.", "difficulty_level": 2}]},
            {"uid": "MET-PUTICIK-TSIKLY", "title": "Циклы и ацикличность",
             "description": "Цикл — замкнутый путь без повторения рёбер. Ациклический граф — DAG (не имеет циклов). Топологическая сортировка DAG. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-PUTICIK-TSIK-1", "title": "Наличие цикла", "statement": "Рёбра: 1→2, 2→3, 3→1. Есть ли цикл?", "solution": "Да: 1→2→3→1.", "difficulty_level": 1}]},
            {"uid": "MET-PUTICIK-MATRITSA", "title": "Матрица смежности и достижимости",
             "description": "Матрица смежности A: aᵢⱼ=1 если есть ребро (i,j). Aⁿ: (Aⁿ)ᵢⱼ = число путей длины n. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-PUTICIK-MATR-1", "title": "Матрица смежности", "statement": "3 вершины, рёбра (1,2),(2,3),(1,3). Матрица?", "solution": "A = [[0,1,1],[1,0,1],[1,1,0]] (неориентированный).", "difficulty_level": 1}]},
        ]),
        ("TOP-BULEVY-FUNKTSII-30a3b0", "SKL-BULEVY-FUNK-SEED", "Булевы функции", [
            {"uid": "MET-BULFUNK-OPRED", "title": "Определение булевой функции",
             "description": "f: {0,1}ⁿ → {0,1}. Всего 2^(2ⁿ) булевых функций от n переменных. Способы задания: таблица, формула, полином Жегалкина. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-BULFUNK-OPR-1", "title": "Число булевых функций", "statement": "Сколько булевых функций от 2 переменных?", "solution": "2^(2²) = 2⁴ = 16 функций.", "difficulty_level": 1}]},
            {"uid": "MET-BULFUNK-POLN-SISTEMA", "title": "Полные системы функций",
             "description": "Система полна, если любую функцию можно выразить через неё. {∧,∨,¬} — полная. {↑} (штрих Шеффера) — полная. {∧,⊕,1} — полная. Теорема Поста. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-BULFUNK-POLN-1", "title": "Выражение через NAND", "statement": "Выразите ¬A через штрих Шеффера (A↑B = ¬(A∧B)).", "solution": "A↑A = ¬(A∧A) = ¬A.", "difficulty_level": 2}]},
            {"uid": "MET-BULFUNK-ZHEGALKIN", "title": "Полином Жегалкина",
             "description": "Каждая булева функция единственным образом представима как ⊕-полином: f = a₀ ⊕ a₁x₁ ⊕ a₂x₂ ⊕ a₁₂x₁x₂ ⊕ ... Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-BULFUNK-ZHEG-1", "title": "Полином Жегалкина", "statement": "Найдите полином Жегалкина для A∨B.", "solution": "A∨B = A⊕B⊕AB. Проверка: 0∨0=0, 0⊕0⊕0=0 ✓; 1∨1=1, 1⊕1⊕1=1 ✓.", "difficulty_level": 2}]},
        ]),
        ("TOP-ZAKONY-BULEVOJ-ALGEBRY-893ed4", "SKL-ZAKONY-BOOL-SEED", "Законы булевой алгебры", [
            {"uid": "MET-BOOLZAK-OSNOV", "title": "Основные законы булевой алгебры",
             "description": "Коммутативность, ассоциативность, дистрибутивность, идемпотентность (A∧A=A), поглощение (A∧(A∨B)=A), де Морган. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-BOOLZAK-OSN-1", "title": "Упрощение", "statement": "Упростите: (A∧B)∨(A∧¬B).", "solution": "A∧(B∨¬B) = A∧1 = A.", "difficulty_level": 1}]},
            {"uid": "MET-BOOLZAK-MINIMIZ", "title": "Минимизация булевых выражений",
             "description": "Карта Карно: для 2-4 переменных, группировка соседних единиц в прямоугольники 1×2, 2×2, 2×4. Склеивание: AB∨A¬B = A. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-BOOLZAK-MIN-1", "title": "Карта Карно", "statement": "f(A,B) = 1 при (0,0),(0,1),(1,1). Минимизируйте.", "solution": "Карно: столбец A=0 полный → ¬A. Клетка (1,1) → A∧B. f = ¬A ∨ (A∧B) = ¬A ∨ B.", "difficulty_level": 2}]},
            {"uid": "MET-BOOLZAK-PRIMENENIE", "title": "Применение в логических схемах",
             "description": "Логические вентили: AND, OR, NOT, XOR, NAND, NOR. Комбинационная схема реализует булеву функцию. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-BOOLZAK-PRIM-1", "title": "Логическая схема", "statement": "Составьте схему для f = A⊕B (XOR).", "solution": "f = (A∧¬B) ∨ (¬A∧B). Два AND, два NOT, один OR. Или: (A∨B) ∧ ¬(A∧B).", "difficulty_level": 2}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 9, "uc_max": 11, "methods": methods}])

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Комбинаторика и вероятность  (29 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _probability_all_ops() -> list[dict]:
    ops: list[dict] = []

    # --- 5-7 кл topics ---
    for uid, skl_uid, title, uc_min, uc_max, methods in [
        ("TOP-OPREDELENIE-VEROYATNOSTI-f1aab2", "SKL-OPRED-VER-SEED", "Определение вероятности", 5, 7, [
            {"uid": "MET-OPRVER-KLASSICH", "title": "Классическое определение вероятности",
             "description": "P(A) = m/n (m — благоприятные исходы, n — все равновозможные). 0 ≤ P ≤ 1. Мерзляк А.Г. 6 кл.",
             "examples": [{"uid": "EX-OPRVER-KLAS-1", "title": "Классическая вероятность", "statement": "В коробке 3 красных и 5 синих шара. Вероятность красного?", "solution": "P = 3/8 = 0.375.", "difficulty_level": 1}]},
            {"uid": "MET-OPRVER-OPYT", "title": "Случайный эксперимент и исходы",
             "description": "Элементарный исход — простейший результат опыта. Пространство элементарных исходов Ω — множество всех возможных. Событие — подмножество Ω. Мерзляк А.Г. 6 кл.",
             "examples": [{"uid": "EX-OPRVER-OPYT-1", "title": "Элементарные исходы", "statement": "Бросок двух монет. Перечислите Ω.", "solution": "Ω = {ОО, ОР, РО, РР}. |Ω| = 4.", "difficulty_level": 1}]},
            {"uid": "MET-OPRVER-GEOM", "title": "Геометрическая вероятность",
             "description": "P = S_благоприятное / S_всё (или длина, объём). Применяется когда исходы непрерывны. Мерзляк А.Г. 7 кл.",
             "examples": [{"uid": "EX-OPRVER-GEOM-1", "title": "Геометрическая вероятность", "statement": "Точка случайно выбирается на отрезке [0;10]. P(попасть в [3;7])?", "solution": "P = 4/10 = 0.4.", "difficulty_level": 1}]},
        ]),
        ("TOP-SOBYTIYA-I-IH-KLASSIFIKA-97f448", "SKL-SOBYT-KLASS-SEED", "События и их классификация", 5, 7, [
            {"uid": "MET-SOBKL-VIDY", "title": "Виды событий: достоверное, невозможное, случайное",
             "description": "Достоверное: P=1 (всегда происходит). Невозможное: P=0. Случайное: 0<P<1. Противоположное событие Ā: P(Ā)=1−P(A). Мерзляк А.Г. 6 кл.",
             "examples": [{"uid": "EX-SOBKL-VID-1", "title": "Тип события", "statement": "В мешке 5 белых шаров. Вынули 1. Какое событие «вынут белый»?", "solution": "Достоверное (P=1, все шары белые).", "difficulty_level": 1}]},
            {"uid": "MET-SOBKL-SOVMEST", "title": "Совместные и несовместные события",
             "description": "Несовместные: A и B не могут произойти одновременно (A∩B=∅). Для несовместных: P(A∪B) = P(A)+P(B). Мерзляк А.Г. 7 кл.",
             "examples": [{"uid": "EX-SOBKL-SOVM-1", "title": "Несовместные события", "statement": "Бросок кубика. A={чётное}, B={нечётное}. Совместны?", "solution": "Нет — число либо чётное, либо нечётное. P(A∪B) = 1/2+1/2 = 1.", "difficulty_level": 1}]},
            {"uid": "MET-SOBKL-POLNAYA", "title": "Полная группа событий",
             "description": "A₁,...,Aₙ — полная группа, если попарно несовместны и P(A₁)+...+P(Aₙ)=1. Мерзляк А.Г. 7 кл.",
             "examples": [{"uid": "EX-SOBKL-POLN-1", "title": "Полная группа", "statement": "Бросок кубика. A₁={1,2}, A₂={3,4}, A₃={5,6}. Полная группа?", "solution": "Попарно несовместны. P(A₁)+P(A₂)+P(A₃) = 1/3+1/3+1/3 = 1. Да.", "difficulty_level": 1}]},
        ]),
        ("TOP-PRAVILA-PODSCHYOTA-db0161", "SKL-PRAVILA-PODSCH-SEED", "Правила подсчёта", 5, 7, [
            {"uid": "MET-PODSCH-UMNOZH", "title": "Правило умножения",
             "description": "Если 1-е действие — m способов, 2-е — n способов, то последовательность двух действий — m·n способов. Мерзляк А.Г. 6 кл.",
             "examples": [{"uid": "EX-PODSCH-UMN-1", "title": "Правило умножения", "statement": "3 блузки и 4 юбки. Сколько нарядов?", "solution": "3 · 4 = 12 нарядов.", "difficulty_level": 1}]},
            {"uid": "MET-PODSCH-SLOZH", "title": "Правило сложения",
             "description": "Если действие можно выполнить m способами ИЛИ n способами (несовместных), то всего m+n. Мерзляк А.Г. 6 кл.",
             "examples": [{"uid": "EX-PODSCH-SLOZH-1", "title": "Правило сложения", "statement": "В библиотеке 5 книг по математике и 3 по физике. Сколько способов взять одну книгу?", "solution": "5 + 3 = 8 способов.", "difficulty_level": 1}]},
            {"uid": "MET-PODSCH-DEREVO", "title": "Дерево возможных вариантов",
             "description": "Строим дерево: каждая ветвь — один выбор. Число листьев = число всех вариантов. Удобно для последовательных выборов. Мерзляк А.Г. 7 кл.",
             "examples": [{"uid": "EX-PODSCH-DER-1", "title": "Дерево вариантов", "statement": "Монету бросают 3 раза. Сколько исходов?", "solution": "2 · 2 · 2 = 8 исходов. Дерево: от корня 2 ветви, от каждой ещё 2, и ещё 2 → 8 листьев.", "difficulty_level": 1}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": uc_min, "uc_max": uc_max, "methods": methods}])

    # --- 7-9 кл topics ---
    for uid, skl_uid, title, methods in [
        ("TOP-OSNOVY-TEORII-VEROYATNOS-c8e176", "SKL-OSNOVY-TEOR-VER-SEED", "Основы теории вероятностей", [
            {"uid": "MET-OSNVER-AKSIOMY", "title": "Аксиоматика вероятности (Колмогоров)",
             "description": "1) P(A)≥0. 2) P(Ω)=1. 3) Для несовместных: P(A∪B)=P(A)+P(B). Следствия: P(∅)=0, P(Ā)=1−P(A). Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-OSNVER-AKS-1", "title": "Аксиомы", "statement": "P(A)=0.3, P(B)=0.5, A и B несовместны. P(A∪B)?", "solution": "P(A∪B) = 0.3 + 0.5 = 0.8.", "difficulty_level": 1}]},
        ]),
        ("TOP-SLUCHAJNYE-SOBYTIYA-f288f9", "SKL-SLUCH-SOBYT-SEED", "Случайные события", [
            {"uid": "MET-SLUCHSOB-ALGEBRA", "title": "Алгебра событий",
             "description": "A∪B (хотя бы одно). A∩B (оба). Ā (не A). A\\B (A, но не B). Законы де Моргана для событий. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-SLUCHSOB-ALG-1", "title": "Алгебра событий", "statement": "Событие: «хотя бы одна 6 при двух бросках». Запишите.", "solution": "A∪B, где A — «6 на 1-м», B — «6 на 2-м». Или: 1 − P(Ā∩B̄) = 1−(5/6)² = 11/36.", "difficulty_level": 2}]},
        ]),
        ("TOP-SVOISTVA-VEROYATNOSTI-51b7ce", "SKL-SVOJSTVA-VER-SEED", "Свойства вероятности", [
            {"uid": "MET-SVVER-FORMULY", "title": "Формула сложения для совместных событий",
             "description": "P(A∪B) = P(A)+P(B)−P(A∩B). Для трёх: +P(A∩B∩C). Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-SVVER-FORM-1", "title": "Сложение вероятностей", "statement": "P(A)=0.6, P(B)=0.5, P(A∩B)=0.3. P(A∪B)?", "solution": "0.6+0.5−0.3 = 0.8.", "difficulty_level": 1}]},
        ]),
        ("TOP-VEROYATNOST-d3cd07", "SKL-VEROYATN-SEED", "Вероятность", [
            {"uid": "MET-VER-STATIST", "title": "Статистическая вероятность",
             "description": "P*(A) = m/n (m — число наступлений A в n опытах). При n→∞ приближается к P(A). Закон больших чисел (интуитивно). Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-VER-STAT-1", "title": "Статистическая вероятность", "statement": "В 500 бросках монеты орёл выпал 260 раз. Стат. вероятность?", "solution": "P* = 260/500 = 0.52 ≈ 0.5 (близко к теоретической).", "difficulty_level": 1}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 7, "uc_max": 9, "methods": methods}])

    # --- 8-9 кл ---
    ops += _build_ops_from_topic_def(
        "TOP-NEZAVISIMYE-SOBYTIYA-bdea5e", "SKL-NEZAV-SOBYT-SEED", "Независимые события",
        [{"uc_min": 8, "uc_max": 9, "methods": [
            {"uid": "MET-NEZSOB-OPRED", "title": "Определение и свойства независимых событий",
             "description": "A и B независимы, если P(A∩B) = P(A)·P(B). Пример: два разных броска кубика. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-NEZSOB-OPR-1", "title": "Независимые события", "statement": "P(A)=0.4, P(B)=0.5, события независимы. P(оба)?", "solution": "P(A∩B) = 0.4 · 0.5 = 0.2.", "difficulty_level": 1}]},
            {"uid": "MET-NEZSOB-SERIYA", "title": "Серия независимых испытаний",
             "description": "n независимых испытаний с P(успеха)=p. P(все успехи) = pⁿ. P(хотя бы 1 успех) = 1−(1−p)ⁿ. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-NEZSOB-SER-1", "title": "Серия испытаний", "statement": "P(попадание)=0.7. 3 выстрела (независимо). P(хотя бы 1)?", "solution": "P = 1−(0.3)³ = 1−0.027 = 0.973.", "difficulty_level": 2}]},
        ]}],
    )

    # --- 9-11 кл topics ---
    for uid, skl_uid, title, methods in [
        ("TOP-USLOVNAYA-VEROYATNOST-8ea76c", "SKL-USLOV-VER-SEED", "Условная вероятность", [
            {"uid": "MET-USLVER-OPRED", "title": "Формула условной вероятности",
             "description": "P(B|A) = P(A∩B)/P(A). Формула полной вероятности: P(B) = ΣP(B|Aᵢ)P(Aᵢ). Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-USLVER-OPR-1", "title": "Условная вероятность", "statement": "P(A)=0.4, P(A∩B)=0.12. P(B|A)?", "solution": "P(B|A) = 0.12/0.4 = 0.3.", "difficulty_level": 2}]},
        ]),
        ("TOP-PERESTANOVKI-469134", "SKL-PEREST-SEED", "Перестановки", [
            {"uid": "MET-PEREST-FORMULA", "title": "Перестановки и факториал",
             "description": "Pₙ = n! = 1·2·...·n. Перестановка — упорядоченное расположение n элементов. 0! = 1. Мерзляк А.Г. 9 кл.",
             "examples": [{"uid": "EX-PEREST-FORM-1", "title": "Перестановки", "statement": "Сколькими способами 5 книг расставить на полке?", "solution": "P₅ = 5! = 120.", "difficulty_level": 1}]},
        ]),
        ("TOP-RAZMESCHENIYA-382d73", "SKL-RAZMESCH-SEED", "Размещения", [
            {"uid": "MET-RAZMESCH-FORMULA", "title": "Размещения",
             "description": "Aⁿₖ = n!/(n−k)! — выбор k из n с учётом порядка. Мерзляк А.Г. 9 кл.",
             "examples": [{"uid": "EX-RAZMESCH-FORM-1", "title": "Размещения", "statement": "Из 8 спортсменов выбрать 3 на пьедестал. Сколько вариантов?", "solution": "A⁸₃ = 8·7·6 = 336.", "difficulty_level": 1}]},
        ]),
        ("TOP-SOCHETANIYA-01b667", "SKL-SOCHET-SEED", "Сочетания", [
            {"uid": "MET-SOCHET-FORMULA", "title": "Формула сочетаний",
             "description": "Cⁿₖ = n!/(k!(n−k)!). Выбор k из n без учёта порядка. Cⁿₖ = Cⁿₙ₋ₖ. Бином Ньютона: (a+b)ⁿ = Σ Cⁿₖ aⁿ⁻ᵏbᵏ. Мерзляк А.Г. 9 кл.",
             "examples": [{"uid": "EX-SOCHET-FORM-1", "title": "Сочетания", "statement": "Из 10 учеников выбрать 3 в команду. Сколько?", "solution": "C¹⁰₃ = 10!/(3!·7!) = 120.", "difficulty_level": 1}]},
        ]),
        ("TOP-KOMBINATORIKA-V-VEROYATN-88900f", "SKL-KOMB-VER-SEED", "Комбинаторика в вероятности", [
            {"uid": "MET-KOMBVER-PRIMENEN", "title": "Применение комбинаторики для подсчёта вероятностей",
             "description": "P = число благоприятных/число всех. Благоприятные и все считаем через Cⁿₖ, Aⁿₖ, Pₙ. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-KOMBVER-PRIM-1", "title": "Комбинаторная вероятность", "statement": "Из 52 карт выбирают 2. P(обе туза)?", "solution": "C⁴₂/C⁵²₂ = 6/1326 = 1/221 ≈ 0.0045.", "difficulty_level": 2}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 9, "uc_max": 11, "methods": methods}])

    # --- 10-11 кл advanced probability topics (compact) ---
    _adv_prob_topics = [
        ("TOP-FORMULA-BAJESA-9e1a3f", "SKL-FORM-BAYES-SEED", "Формула Байеса", [
            {"uid": "MET-BAYES-FORM", "title": "Формула Байеса",
             "description": "P(Aᵢ|B) = P(B|Aᵢ)P(Aᵢ) / ΣP(B|Aⱼ)P(Aⱼ). Пересчёт вероятностей гипотез после наблюдения. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-BAYES-1", "title": "Байес", "statement": "Болезнь: P=0.01. Тест: чувств. 0.99, специф. 0.95. P(болен|тест+)?", "solution": "P(+|B)P(B)/[P(+|B)P(B)+P(+|Z)P(Z)] = 0.99·0.01/(0.99·0.01+0.05·0.99) = 0.0099/0.0594 ≈ 0.167.", "difficulty_level": 3}]},
        ]),
        ("TOP-SLUCHAINYE-VELICHINY-90d9e2", "SKL-SLUCH-VELICH-SEED", "Случайные величины", [
            {"uid": "MET-SLUCHVEL-ZAKRASPR", "title": "Закон распределения дискретной СВ",
             "description": "Таблица xᵢ → pᵢ. Σpᵢ = 1. Функция распределения F(x) = P(X < x). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-SLUCHVEL-ZAK-1", "title": "Закон распределения", "statement": "X — число орлов при 2 бросках. Закон распределения?", "solution": "X=0: P=1/4. X=1: P=1/2. X=2: P=1/4.", "difficulty_level": 1}]},
        ]),
        ("TOP-MATEMATICHESKOE-OZHIDANI-d5d8c8", "SKL-MAT-OZHID-SEED", "Математическое ожидание", [
            {"uid": "MET-MATOZH-FORMULA", "title": "Формула математического ожидания",
             "description": "E(X) = Σxᵢpᵢ. Свойства: E(aX+b) = aE(X)+b. E(X+Y) = E(X)+E(Y). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-MATOZH-FORM-1", "title": "Мат. ожидание", "statement": "Кубик: X — число очков. E(X)?", "solution": "E(X) = (1+2+3+4+5+6)/6 = 21/6 = 3.5.", "difficulty_level": 1}]},
        ]),
        ("TOP-DISPERSIYA-I-STANDARTNOE-15d0f1", "SKL-DISP-STAND-SEED", "Дисперсия и стандартное отклонение", [
            {"uid": "MET-DISP-FORMULA", "title": "Формула дисперсии",
             "description": "D(X) = E(X²) − (E(X))² = Σ(xᵢ−E(X))²pᵢ. σ = √D. D(aX+b) = a²D(X). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-DISP-FORM-1", "title": "Дисперсия", "statement": "X: 1,2,3 с P: 1/6,1/2,1/3. D(X)?", "solution": "E(X) = 1/6+1+1 = 13/6 ≈ 2.17. E(X²) = 1/6+2+3 = 31/6. D = 31/6−169/36 = 17/36 ≈ 0.47.", "difficulty_level": 2}]},
        ]),
    ]

    # Many 10-11 topics with single-method compact definition
    _adv_prob_topics += [
        ("TOP-RASPREDELENIE-VEROYATNOS-4c5863", "SKL-RASPR-VER-SEED", "Распределение вероятностей", [
            {"uid": "MET-RASPRVER-VIDY", "title": "Виды распределений: дискретные и непрерывные",
             "description": "Дискретное: конечное/счётное множество значений. Непрерывное: плотность f(x), P(a<X<b) = ∫f(x)dx. Функция распределения: F(x) = P(X<x). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-RASPRVER-1", "title": "Плотность", "statement": "f(x) = 2x на [0;1], 0 иначе. P(0.5<X<1)?", "solution": "∫₀.₅¹ 2x dx = x²|₀.₅¹ = 1 − 0.25 = 0.75.", "difficulty_level": 2}]},
        ]),
        ("TOP-VVEDENIE-V-VEROYATNOSTNY-e344b3", "SKL-VVED-VERMOD-SEED", "Введение в вероятностные модели", [
            {"uid": "MET-VVEDVERMOD-OPRED", "title": "Вероятностные модели",
             "description": "Модель Бернулли: n испытаний, P(k успехов) = Cⁿₖpᵏqⁿ⁻ᵏ. Модель случайного блуждания: последовательность шагов ±1. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-VVEDVERMOD-1", "title": "Модель Бернулли", "statement": "5 бросков монеты. P(ровно 3 орла)?", "solution": "C⁵₃·(0.5)³·(0.5)² = 10·0.03125 = 0.3125.", "difficulty_level": 2}]},
        ]),
        ("TOP-RASPREDELENIE-BERNULLI-I-2654ca", "SKL-RASPR-BERN-SEED", "Распределение Бернулли", [
            {"uid": "MET-RASPRBERN-FORM", "title": "Распределение Бернулли и биномиальное",
             "description": "X~Bern(p): P(1)=p, P(0)=q. Биномиальное: X~Bin(n,p), P(k) = Cⁿₖpᵏqⁿ⁻ᵏ. E=np, D=npq. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-RASPRBERN-1", "title": "Биномиальное", "statement": "n=10, p=0.3. E(X)? D(X)?", "solution": "E = 10·0.3 = 3. D = 10·0.3·0.7 = 2.1. σ ≈ 1.45.", "difficulty_level": 2}]},
        ]),
        ("TOP-RASPREDELENIE-PUASSONA-66bdaa", "SKL-RASPR-PUASS-SEED", "Распределение Пуассона", [
            {"uid": "MET-RASPRPUASS-FORM", "title": "Формула Пуассона",
             "description": "X~Pois(λ): P(k) = λᵏe⁻λ/k!. E=D=λ. Приближение биномиального при n→∞, p→0, np→λ. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-RASPRPUASS-1", "title": "Пуассон", "statement": "В среднем 2 ошибки на страницу. P(0 ошибок)?", "solution": "P(0) = 2⁰·e⁻²/0! = e⁻² ≈ 0.135.", "difficulty_level": 2}]},
        ]),
        ("TOP-DISKRETNYE-VEROYATNOSTNY-450411", "SKL-DISKR-VERMOD-SEED", "Дискретные вероятностные модели", [
            {"uid": "MET-DISKRVERMOD-GEOM", "title": "Геометрическое распределение",
             "description": "X~Geom(p): P(k)=q^(k-1)p (номер первого успеха). E=1/p, D=q/p². Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-DISKRVERMOD-1", "title": "Геометрическое", "statement": "P(успех)=0.2. E(число попыток до первого успеха)?", "solution": "E = 1/0.2 = 5 попыток.", "difficulty_level": 1}]},
        ]),
        ("TOP-NEPRERYVNYE-VEROYATNOSTN-236631", "SKL-NEPR-VERMOD-SEED", "Непрерывные вероятностные модели", [
            {"uid": "MET-NEPRVERMOD-RAVNOM", "title": "Равномерное непрерывное распределение",
             "description": "X~U(a,b): f(x)=1/(b−a) на [a,b]. E=(a+b)/2, D=(b−a)²/12. P(c<X<d)=(d−c)/(b−a). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-NEPRVERMOD-1", "title": "Равномерное", "statement": "X~U(0,10). P(3<X<7)?", "solution": "P = (7−3)/10 = 0.4.", "difficulty_level": 1}]},
        ]),
        ("TOP-NORMALNOE-RASPREDELENIE-ce0938", "SKL-NORM-RASPR-SEED", "Нормальное распределение", [
            {"uid": "MET-NORMRASPR-FORM", "title": "Нормальное распределение N(μ,σ²)",
             "description": "f(x) = (1/(σ√2π))e^(−(x−μ)²/(2σ²)). Правило 68-95-99.7: P(μ±σ)≈0.68, P(μ±2σ)≈0.95. Z-оценка: Z=(X−μ)/σ. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-NORMRASPR-1", "title": "Правило 3σ", "statement": "Рост: μ=170, σ=10. P(150<X<190)?", "solution": "(150−170)/10=−2, (190−170)/10=2. P(|Z|<2) ≈ 0.95.", "difficulty_level": 2}]},
        ]),
        ("TOP-EKSPONENCIALNOE-RASPREDE-a30410", "SKL-EKS-RASPR-SEED", "Экспоненциальное распределение", [
            {"uid": "MET-EKSRASPR-FORM", "title": "Экспоненциальное распределение Exp(λ)",
             "description": "f(x) = λe⁻λˣ (x≥0). F(x) = 1−e⁻λˣ. E=1/λ, D=1/λ². Свойство отсутствия памяти. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-EKSRASPR-1", "title": "Экспоненциальное", "statement": "Среднее время обслуживания 5 мин (λ=1/5). P(X>10)?", "solution": "P(X>10) = e⁻¹⁰/⁵ = e⁻² ≈ 0.135.", "difficulty_level": 2}]},
        ]),
        ("TOP-PRIMENENIE-VEROYATNOSTNY-3216ba", "SKL-PRIMEN-VER-SEED", "Применение вероятностных моделей", [
            {"uid": "MET-PRIMENVER-ZADACHI", "title": "Решение прикладных задач",
             "description": "Выбор модели (Бернулли, Пуассон, нормальная). Формулировка в терминах вероятностей. Интерпретация результата. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PRIMENVER-1", "title": "Прикладная задача", "statement": "Завод: 2% брака. Из партии 100 штук. P(не более 3 бракованных)?", "solution": "X~Bin(100,0.02) ≈ Pois(2). P(X≤3) = e⁻²(1+2+2+4/3) ≈ 0.857.", "difficulty_level": 2}]},
        ]),
        ("TOP-CENTRALNAYA-PREDELNAYA-T-b48f16", "SKL-CENTR-PRED-SEED", "Центральная предельная теорема", [
            {"uid": "MET-CPT-FORMUL", "title": "ЦПТ: сумма большого числа СВ → нормальное",
             "description": "Если X₁,...,Xₙ независимы одинаково распределены, E=μ, D=σ², то (Σ−nμ)/(σ√n) → N(0,1). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-CPT-1", "title": "ЦПТ", "statement": "100 бросков кубика. P(сумма > 370)?", "solution": "μ=3.5, σ²=35/12. E(S)=350, σ(S)=√(100·35/12)≈17.1. Z=(370−350)/17.1≈1.17. P(Z>1.17)≈0.121.", "difficulty_level": 3}]},
        ]),
        ("TOP-ZAKON-BOLSHIH-CHISEL-efc36b", "SKL-ZAK-BOLSH-CHIS-SEED", "Закон больших чисел", [
            {"uid": "MET-ZBC-FORM", "title": "Закон больших чисел (Бернулли, Чебышёв)",
             "description": "Среднее арифметическое X̄ₙ → E(X) при n→∞ (по вероятности). Неравенство Чебышёва: P(|X−E(X)|≥ε) ≤ D(X)/ε². Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-ZBC-1", "title": "Закон больших чисел", "statement": "X~Bern(0.5). 1000 испытаний. P(|X̄−0.5|>0.05)?", "solution": "Чебышёв: P ≤ D/(n·ε²) = 0.25/(1000·0.0025) = 0.1. Фактически гораздо меньше.", "difficulty_level": 2}]},
        ]),
        ("TOP-MODELIROVANIE-SLUCHAINYH-ddc404", "SKL-MODEL-SLUCH-SEED", "Моделирование случайных процессов", [
            {"uid": "MET-MODSLUCH-MONTEKARLO", "title": "Метод Монте-Карло",
             "description": "Приближённое вычисление через случайное моделирование. Генерация случайных чисел, подсчёт доли «попаданий». Точность ∝ 1/√n. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-MODSLUCH-1", "title": "Монте-Карло для π", "statement": "Случайные точки в квадрате [0,1]². Доля внутри четверти круга → ?", "solution": "P(x²+y²≤1) = π/4. π ≈ 4·(число попаданий)/(число точек).", "difficulty_level": 2}]},
        ]),
    ]

    for uid, skl_uid, title, methods in _adv_prob_topics:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 10, "uc_max": 11, "methods": methods}])

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: Статистика  (26 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _statistics_ops() -> list[dict]:
    ops: list[dict] = []

    # 7-9 кл stats topics (compact loop)
    _stats_79 = [
        ("TOP-MERY-CENTRALNOI-TENDENCI-75dcdc", "SKL-MERY-CENTR-SEED", "Меры центральной тенденции", [
            {"uid": "MET-MERCENT-SREDNEE", "title": "Среднее, медиана, мода",
             "description": "Среднее: x̄ = Σxᵢ/n. Медиана: середина упорядоченного ряда. Мода: самое частое значение. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-MERCENT-1", "title": "Среднее, медиана, мода", "statement": "Данные: 3, 5, 5, 7, 10. Найдите среднее, медиану, моду.", "solution": "Среднее = 30/5 = 6. Медиана = 5 (3-й элемент). Мода = 5 (встречается дважды).", "difficulty_level": 1}]},
        ]),
        ("TOP-MERY-RAZBROSA-c487ac", "SKL-MERY-RAZBR-SEED", "Меры разброса", [
            {"uid": "MET-MERRAZB-RAZMAX", "title": "Размах, дисперсия, стандартное отклонение",
             "description": "Размах R = max − min. Дисперсия D = Σ(xᵢ−x̄)²/n. σ = √D. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-MERRAZB-1", "title": "Размах", "statement": "Данные: 2, 4, 6, 8, 10. Размах?", "solution": "R = 10 − 2 = 8.", "difficulty_level": 1}]},
        ]),
        ("TOP-SREDNIE-HARAKTERISTIKI-b231f6", "SKL-SRED-HARAKT-SEED", "Средние характеристики", [
            {"uid": "MET-SREDHAR-VZVESHAN", "title": "Средневзвешенное и средние степенные",
             "description": "Взвешенное: x̄w = Σwᵢxᵢ/Σwᵢ. Средне-геометрическое: (x₁·x₂·...·xₙ)^(1/n). Средне-гармоническое: n/(Σ1/xᵢ). Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-SREDHAR-1", "title": "Средневзвешенное", "statement": "Оценки: 5(вес 3), 4(вес 2), 3(вес 1). Средневзвешенная?", "solution": "(5·3+4·2+3·1)/(3+2+1) = 26/6 ≈ 4.33.", "difficulty_level": 1}]},
        ]),
        ("TOP-RAZBROS-ac7a78", "SKL-RAZBROS-SEED", "Разброс", [
            {"uid": "MET-RAZBROS-KVARTILI", "title": "Квартили и межквартильный размах",
             "description": "Q₁ — 25-й перцентиль, Q₂ — медиана, Q₃ — 75-й перцентиль. IQR = Q₃ − Q₁. Выбросы: x < Q₁−1.5·IQR или x > Q₃+1.5·IQR. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-RAZBROS-1", "title": "IQR", "statement": "Данные: 2,3,5,7,8,9,12. Q₁? Q₃? IQR?", "solution": "Q₁=3, Q₃=9. IQR = 9−3 = 6.", "difficulty_level": 1}]},
        ]),
        ("TOP-OSNOVNYE-PONYATIYA-STATI-2d24ef", "SKL-OSNPONYAT-STAT-SEED", "Основные понятия статистики", [
            {"uid": "MET-OSNSTAT-OPRED", "title": "Генеральная совокупность и выборка",
             "description": "Генеральная совокупность — все объекты. Выборка — часть для изучения. Репрезентативность — выборка отражает свойства совокупности. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-OSNSTAT-1", "title": "Выборка", "statement": "Проверка качества лампочек на заводе. Из 10000 проверили 200. Что ген. совокупность, что выборка?", "solution": "Ген. совокупность: 10000 лампочек. Выборка: 200 проверенных.", "difficulty_level": 1}]},
        ]),
        ("TOP-TIPY-DANNYH-I-UROVNI-IZM-c9a86a", "SKL-TIPYDAN-SEED", "Типы данных и уровни измерения", [
            {"uid": "MET-TIPDAN-SHKAL", "title": "Шкалы измерения",
             "description": "Номинальная (категории). Порядковая (ранг). Интервальная (разности). Относительная (отношения). Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-TIPDAN-1", "title": "Шкалы", "statement": "Цвет глаз, школьная оценка, температура (°C), вес (кг). Какие шкалы?", "solution": "Номинальная, порядковая, интервальная, относительная.", "difficulty_level": 1}]},
        ]),
        ("TOP-SBOR-DANNYH-METODY-I-INS-60afe1", "SKL-SBORDAN-SEED", "Сбор данных: методы и инструменты", [
            {"uid": "MET-SBORDAN-METODY", "title": "Методы сбора: опрос, наблюдение, эксперимент",
             "description": "Опрос (анкета). Наблюдение (фиксация без вмешательства). Эксперимент (контролируемые условия). Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-SBORDAN-1", "title": "Метод сбора", "statement": "Изучают влияние музыки на концентрацию. Какой метод?", "solution": "Эксперимент (контрольная и экспериментальная группы).", "difficulty_level": 1}]},
        ]),
        ("TOP-OPISANIE-DANNYH-MERY-CEN-4cff59", "SKL-OPISDAN-CEN-SEED", "Описание данных: меры центра", [
            {"uid": "MET-OPISDAN-CENTR", "title": "Сравнение мер центральной тенденции",
             "description": "Среднее чувствительно к выбросам. Медиана устойчива. Мода для категориальных. Для симметричных распределений все три близки. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-OPISDAN-CEN-1", "title": "Выбор меры", "statement": "Зарплаты: 20, 25, 30, 30, 500 тыс. Какая мера лучше?", "solution": "Среднее = 121, медиана = 30. Медиана лучше (не искажена выбросом 500).", "difficulty_level": 1}]},
        ]),
        ("TOP-OPISANIE-DANNYH-MERY-RAZ-65807e", "SKL-OPISDAN-RAZ-SEED", "Описание данных: меры разброса", [
            {"uid": "MET-OPISDAN-RAZB", "title": "Коэффициент вариации",
             "description": "CV = σ/x̄ · 100%. Относительная мера разброса. Позволяет сравнивать разброс величин разного масштаба. Макарычев Ю.Н. 9 кл.",
             "examples": [{"uid": "EX-OPISDAN-RAZ-1", "title": "Коэффициент вариации", "statement": "Рост: x̄=170, σ=10. Вес: x̄=70, σ=15. Что более вариативно?", "solution": "CV_рост = 10/170 ≈ 5.9%. CV_вес = 15/70 ≈ 21.4%. Вес более вариативен.", "difficulty_level": 1}]},
        ]),
        ("TOP-GRAFICHESKOE-PREDSTAVLEN-c2da9b", "SKL-GRAF-PREDST-SEED", "Графическое представление данных", [
            {"uid": "MET-GRAFPREDST-VIDY", "title": "Виды графиков и диаграмм",
             "description": "Столбчатая (сравнение категорий). Круговая (доли). Гистограмма (частоты интервалов). Полигон частот. Box-plot. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-GRAFPREDST-1", "title": "Выбор графика", "statement": "Нужно показать доли расходов семьи. Какой график?", "solution": "Круговая диаграмма (показывает доли целого).", "difficulty_level": 1}]},
        ]),
        ("TOP-VIZUALIZACIYA-DANNYH-GRA-d211d6", "SKL-VIZDAN-SEED", "Визуализация данных", [
            {"uid": "MET-VIZDAN-GISTOGRAMMA", "title": "Построение гистограммы",
             "description": "Разбиваем данные на интервалы. Высота столбца = частота (или относительная частота). Площадь = 1 для плотности. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-VIZDAN-1", "title": "Гистограмма", "statement": "Данные: 2,3,5,5,6,7,8,8,8,9. Интервалы [2;5), [5;8), [8;10). Частоты?", "solution": "[2;5): 2 (числа 2,3). [5;8): 4 (числа 5,5,6,7). [8;10): 4 (числа 8,8,8,9).", "difficulty_level": 1}]},
        ]),
        ("TOP-RABOTA-S-DANNYMI-005", "SKL-RABDAN-SEED", "Работа с данными", [
            {"uid": "MET-RABDAN-TABLICA", "title": "Чтение и анализ таблиц данных",
             "description": "Частотная таблица: значение → частота/относительная частота. Накопленная частота. Группированные данные. Макарычев Ю.Н. 7 кл.",
             "examples": [{"uid": "EX-RABDAN-1", "title": "Частотная таблица", "statement": "Оценки: 3,4,5,4,5,3,4,4,5,4. Постройте частотную таблицу.", "solution": "3: 2 (20%). 4: 5 (50%). 5: 3 (30%).", "difficulty_level": 1}]},
        ]),
        ("TOP-VVEDENIE-V-OPISATELNUYU--a52049", "SKL-VVED-OPIS-SEED", "Введение в описательную статистику", [
            {"uid": "MET-VVEDOPIS-PLAN", "title": "Этапы статистического исследования",
             "description": "1) Постановка задачи. 2) Сбор данных. 3) Обработка (очистка, группировка). 4) Анализ (описательная статистика). 5) Выводы. Макарычев Ю.Н. 8 кл.",
             "examples": [{"uid": "EX-VVEDOPIS-1", "title": "Этапы", "statement": "Исследование успеваемости. Перечислите этапы.", "solution": "1) Цель: связь времени занятий и оценок. 2) Анкетирование учеников. 3) Таблица данных. 4) Среднее, корреляция. 5) Вывод о связи.", "difficulty_level": 1}]},
        ]),
    ]

    for uid, skl_uid, title, methods in _stats_79:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 7, "uc_max": 9, "methods": methods}])

    # 8-11 single topic
    ops += _build_ops_from_topic_def(
        "TOP-SVODNYE-TABLICY-c6cff5", "SKL-SVODN-TABL-SEED", "Сводные таблицы",
        [
            {"uc_min": 8, "uc_max": 9, "methods": [
                {"uid": "MET-SVTABL-POSTROENIE-89", "title": "Построение и чтение сводных таблиц",
                 "description": "Таблица сопряжённости: строки — один признак, столбцы — другой, значения — частоты. Итоги по строкам/столбцам. Макарычев Ю.Н. 8 кл.",
                 "examples": [{"uid": "EX-SVTABL-89-1", "title": "Таблица сопряжённости", "statement": "30 учеников: мальчиков 18 (12 любят математику), девочек 12 (8 любят). Постройте таблицу.", "solution": "М: мат=12, не мат=6, итого=18. Д: мат=8, не мат=4, итого=12. Всего: мат=20, не мат=10.", "difficulty_level": 1}]},
            ]},
            {"uc_min": 10, "uc_max": 11, "methods": [
                {"uid": "MET-SVTABL-ANALIZ-1011", "title": "Анализ многомерных данных",
                 "description": "Перекрёстные таблицы для выявления связей. Условные распределения. Критерий χ² для проверки независимости. Колмогоров А.Н. 10-11 кл.",
                 "examples": [{"uid": "EX-SVTABL-1011-1", "title": "Условное распределение", "statement": "Из таблицы: 20 из 30 любят математику. Среди мальчиков: 12/18=67%. Среди девочек: 8/12=67%. Связаны ли?", "solution": "Доли одинаковы → пол и любовь к математике не связаны.", "difficulty_level": 2}]},
            ]},
        ],
    )

    # 9-11 кл
    for uid, skl_uid, title, methods in [
        ("TOP-INTERPRETACIYA-STATISTIC-460db0", "SKL-INTERPR-STAT-SEED", "Интерпретация статистических данных", [
            {"uid": "MET-INTSTAT-OSHIBKI", "title": "Типичные ошибки интерпретации",
             "description": "Корреляция ≠ причинность. Выбросы искажают среднее. Малая выборка ненадёжна. Ошибка выжившего. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-INTSTAT-1", "title": "Ошибка интерпретации", "statement": "Рост продаж мороженого и утоплений коррелируют. Мороженое опасно?", "solution": "Нет, корреляция через скрытый фактор — жару. Корреляция ≠ причинность.", "difficulty_level": 1}]},
        ]),
        ("TOP-PRIMENENIE-STATISTIKI-V--dcd30e", "SKL-PRIMEN-STAT-SEED", "Применение статистики", [
            {"uid": "MET-PRIMSTAT-ZADACHI", "title": "Статистика в реальных задачах",
             "description": "Демография, экономика, медицина, образование. Анализ трендов, прогнозирование. Визуализация для принятия решений. Мерзляк А.Г. 9-11 кл.",
             "examples": [{"uid": "EX-PRIMSTAT-1", "title": "Анализ тренда", "statement": "Температуры за 5 лет: 15.1, 15.3, 15.2, 15.5, 15.8°C. Тренд?", "solution": "Восходящий тренд. Линейная регрессия: ~+0.15°C/год.", "difficulty_level": 1}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 9, "uc_max": 11, "methods": methods}])

    # 10-11 кл advanced stats (compact)
    _stats_1011 = [
        ("TOP-KOEFFICIENTY-ASIMMETRII--55d6ee", "SKL-KOEFF-ASIM-SEED", "Коэффициенты асимметрии", [
            {"uid": "MET-KOEFFASIM-FORM", "title": "Асимметрия и эксцесс",
             "description": "Асимметрия (skewness): γ₁ = E((X−μ)³)/σ³. >0 — правый хвост, <0 — левый. Эксцесс (kurtosis): γ₂ = E((X−μ)⁴)/σ⁴ − 3. Нормальное: γ₁=0, γ₂=0. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-KOEFFASIM-1", "title": "Асимметрия", "statement": "Распределение доходов — правая асимметрия. Что это значит?", "solution": "Длинный правый хвост: большинство доходов ниже среднего, мало очень высоких. Среднее > медианы.", "difficulty_level": 2}]},
        ]),
        ("TOP-VYBORKA-3370b5", "SKL-VYBORKA-SEED", "Выборка", [
            {"uid": "MET-VYBORKA-METODY", "title": "Методы формирования выборки",
             "description": "Простая случайная, стратифицированная, кластерная, систематическая. Репрезентативность. Ошибка выборки. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-VYBORKA-1", "title": "Стратифицированная выборка", "statement": "1000 студентов: 600 гум., 400 тех. Выборка 100. Как стратифицировать?", "solution": "60 из гуманитариев, 40 из технарей (пропорционально).", "difficulty_level": 1}]},
        ]),
        ("TOP-VYBORKA-I-POPULYACIYA-471a66", "SKL-VYB-POPUL-SEED", "Выборка и популяция", [
            {"uid": "MET-VYBPOP-OTSENKI", "title": "Точечные оценки параметров",
             "description": "x̄ — оценка μ. s² — оценка σ². Несмещённость: E(θ̂)=θ. Состоятельность: θ̂→θ при n→∞. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-VYBPOP-1", "title": "Несмещённая оценка", "statement": "Почему делим на n−1, а не n для выборочной дисперсии?", "solution": "s² = Σ(xᵢ−x̄)²/(n−1) — несмещённая оценка σ². Деление на n даёт заниженную оценку.", "difficulty_level": 2}]},
        ]),
        ("TOP-OSHIBKI-VYBORKI-024504", "SKL-OSHIBKI-VYB-SEED", "Ошибки выборки", [
            {"uid": "MET-OSHVYB-DOVERIT", "title": "Доверительный интервал",
             "description": "x̄ ± z·σ/√n (95%: z=1.96). Ширина ∝ 1/√n. Интерпретация: «95% таких интервалов содержат μ». Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-OSHVYB-1", "title": "Доверительный интервал", "statement": "n=100, x̄=50, σ=10. 95% доверительный интервал?", "solution": "50 ± 1.96·10/√100 = 50 ± 1.96 = (48.04; 51.96).", "difficulty_level": 2}]},
        ]),
        ("TOP-KORRELYACIONNYI-ANALIZ-d5a590", "SKL-KORR-ANAL-SEED", "Корреляционный анализ", [
            {"uid": "MET-KORRANAL-PEARSON", "title": "Коэффициент корреляции Пирсона",
             "description": "r = Σ(xᵢ−x̄)(yᵢ−ȳ) / √(Σ(xᵢ−x̄)²·Σ(yᵢ−ȳ)²). −1≤r≤1. |r|>0.7 — сильная связь. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-KORRANAL-1", "title": "Интерпретация r", "statement": "r = −0.85 между часами ТВ и оценкой. Интерпретация?", "solution": "Сильная отрицательная корреляция: чем больше ТВ, тем ниже оценка. Но причинность не доказана.", "difficulty_level": 2}]},
        ]),
        ("TOP-KORRELYACIYA-I-REGRESSIY-43dd38", "SKL-KORR-REGR-SEED", "Корреляция и регрессия", [
            {"uid": "MET-KORRREGR-MNK", "title": "Линейная регрессия (МНК)",
             "description": "y = ax + b. a = Σ(xᵢ−x̄)(yᵢ−ȳ)/Σ(xᵢ−x̄)². b = ȳ − ax̄. R² — коэффициент детерминации (доля объяснённой дисперсии). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-KORRREGR-1", "title": "Линейная регрессия", "statement": "x: 1,2,3,4. y: 2,4,5,8. Найдите уравнение.", "solution": "x̄=2.5, ȳ=4.75. Σ(x−x̄)(y−ȳ)=7.5, Σ(x−x̄)²=5. a=1.5, b=4.75−3.75=1.0. y=1.5x+1.", "difficulty_level": 2}]},
        ]),
        ("TOP-KORRELYATSIYA-7d5d50", "SKL-KORRELYATS-SEED", "Корреляция", [
            {"uid": "MET-KORREL-RANGOVAYA", "title": "Ранговая корреляция Спирмена",
             "description": "rₛ = 1 − 6Σdᵢ²/(n(n²−1)), где dᵢ — разность рангов. Для порядковых данных или при выбросах. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-KORREL-1", "title": "Корреляция Спирмена", "statement": "Ранги X: 1,2,3,4. Ранги Y: 1,3,2,4. rₛ?", "solution": "d: 0,−1,1,0. Σd²=2. rₛ = 1−12/(4·15) = 1−0.2 = 0.8.", "difficulty_level": 2}]},
        ]),
        ("TOP-PROVERKA-GIPOTEZ-9511b6", "SKL-PROV-GIPOT-SEED", "Проверка гипотез", [
            {"uid": "MET-PROVGIPOT-OBSHCH", "title": "Общая схема проверки гипотез",
             "description": "H₀ (нулевая) vs H₁ (альтернативная). Уровень значимости α. Статистика критерия. p-value < α → отвергаем H₀. Ошибки I и II рода. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-PROVGIPOT-1", "title": "Проверка гипотезы", "statement": "H₀: μ=100. x̄=103, σ=10, n=25. α=0.05. Отвергнуть?", "solution": "z = (103−100)/(10/5) = 1.5. p ≈ 0.134 > 0.05. Не отвергаем H₀.", "difficulty_level": 2}]},
        ]),
        ("TOP-TESTIROVANIE-GIPOTEZ-S-I-83526e", "SKL-TEST-GIPOT-SEED", "Тестирование гипотез с использованием данных", [
            {"uid": "MET-TESTGIPOT-TSTUDENT", "title": "t-критерий Стьюдента",
             "description": "Для малых выборок (n<30) или неизвестной σ. t = (x̄−μ₀)/(s/√n), df=n−1. Двухвыборочный: t = (x̄₁−x̄₂)/√(s₁²/n₁+s₂²/n₂). Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-TESTGIPOT-1", "title": "t-критерий", "statement": "n=16, x̄=52, s=8, H₀: μ=48. t?", "solution": "t = (52−48)/(8/4) = 2.0. df=15. t_кр(0.05,15) ≈ 2.13. |t|=2.0 < 2.13 → не отвергаем.", "difficulty_level": 2}]},
        ]),
        ("TOP-OCENKA-PARAMETROV-RASPRE-f0b295", "SKL-OCENKA-PARAM-SEED", "Оценка параметров распределения", [
            {"uid": "MET-OCPARAM-MLE", "title": "Метод максимального правдоподобия",
             "description": "L(θ) = ΠP(xᵢ|θ). Максимизируем ln L. Для нормального: θ̂_μ = x̄, θ̂_σ² = Σ(xᵢ−x̄)²/n. Колмогоров А.Н. 10-11 кл.",
             "examples": [{"uid": "EX-OCPARAM-1", "title": "MLE для λ Пуассона", "statement": "Наблюдения: 2,3,1,4,0. MLE для λ?", "solution": "λ̂ = x̄ = (2+3+1+4+0)/5 = 2.0.", "difficulty_level": 2}]},
        ]),
    ]

    for uid, skl_uid, title, methods in _stats_1011:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 10, "uc_max": 11, "methods": methods}])

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# SECTION: ОГЭ + ЕГЭ  (9 topics)
# ═══════════════════════════════════════════════════════════════════════════

def _exam_ops() -> list[dict]:
    ops: list[dict] = []

    # ОГЭ topics (9 кл)
    for uid, skl_uid, title, methods in [
        ("TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026", "SKL-OGE-ANALIZ-SEED", "ОГЭ: Анализ таблиц и диаграмм", [
            {"uid": "MET-OGE-ANALIZ-CHTENIE", "title": "Чтение таблиц и диаграмм",
             "description": "Извлечение данных из столбчатых, круговых диаграмм, таблиц. Вычисление долей, средних. Сравнение показателей. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-ANAL-1", "title": "Чтение диаграммы", "statement": "По диаграмме: в янв. 10°, фев. 15°, мар. 20°. На сколько % выросла температура с янв. по мар.?", "solution": "Рост: (20−10)/10 · 100% = 100%.", "difficulty_level": 1}]},
            {"uid": "MET-OGE-ANALIZ-SRAVNENIE", "title": "Сравнительный анализ данных",
             "description": "Сравнение величин из нескольких источников. Нахождение наибольшего/наименьшего. Определение тенденций. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-ANAL-2", "title": "Сравнение", "statement": "Завод А: 100 деталей/день, Б: 80. За 5 дней А произвёл на сколько больше?", "solution": "(100−80)·5 = 100 деталей.", "difficulty_level": 1}]},
            {"uid": "MET-OGE-ANALIZ-VYCHISLENIYA", "title": "Вычисления по табличным данным",
             "description": "Средние, проценты, пропорции по данным таблицы. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-ANAL-3", "title": "Среднее по таблице", "statement": "Оценки 5 учеников: 4,5,3,4,4. Средний балл?", "solution": "(4+5+3+4+4)/5 = 20/5 = 4.0.", "difficulty_level": 1}]},
        ]),
        ("TOP-OGE-GEOMETRICHESKOE-DOKAZATELSTVO-2026", "SKL-OGE-GEOMDOK-SEED", "ОГЭ: Геометрическое доказательство", [
            {"uid": "MET-OGE-GEOMDOK-PLAN", "title": "Структура геометрического доказательства",
             "description": "1) Записать дано и требуется. 2) Чертёж. 3) Цепочка логических шагов с обоснованием (теорема, аксиома). 4) ЧТД. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-GEOMDOK-1", "title": "Равнобедренный треугольник", "statement": "Докажите: углы при основании равнобедренного треугольника равны.", "solution": "Дано: AB=AC. Проведём медиану AM. △ABM = △ACM (по трём сторонам: AB=AC, BM=MC, AM общая). ∠B = ∠C. ЧТД.", "difficulty_level": 2}]},
            {"uid": "MET-OGE-GEOMDOK-METODY", "title": "Типовые приёмы доказательства",
             "description": "Признаки равенства/подобия треугольников. Свойства параллельных прямых. Вписанные углы. Теорема Пифагора. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-GEOMDOK-2", "title": "Параллельные прямые", "statement": "AB ∥ CD, секущая EF. Докажите ∠AEF = ∠DFE.", "solution": "∠AEF и ∠DFE — накрест лежащие при параллельных AB∥CD и секущей EF → равны.", "difficulty_level": 1}]},
            {"uid": "MET-OGE-GEOMDOK-OKRUZHNOST", "title": "Задачи с окружностью",
             "description": "Вписанные углы, касательные, хорды. Центральный = дуге, вписанный = половине. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-GEOMDOK-3", "title": "Вписанный угол", "statement": "Докажите: вписанный угол = половине центрального, опирающегося на ту же дугу.", "solution": "Случай 1: сторона через центр. △OAB равнобедренный (OA=OB=R). ∠AOB = 2∠OAB (внешний). ∠вписанный = ∠OAB = ∠AOB/2. ЧТД.", "difficulty_level": 2}]},
        ]),
        ("TOP-OGE-PRAKTIKO-ORIENTIROVANNYE-ZADACHI-2026", "SKL-OGE-PRAKT-SEED", "ОГЭ: Практико-ориентированные задачи", [
            {"uid": "MET-OGE-PRAKT-PLAN", "title": "Задачи на планировку",
             "description": "Чтение плана участка/квартиры. Вычисление площадей, расстояний. Масштаб. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-PRAKT-1", "title": "Площадь участка", "statement": "Участок 30×20 м. Дом 10×8 м. Площадь свободной территории?", "solution": "30·20 − 10·8 = 600 − 80 = 520 м².", "difficulty_level": 1}]},
            {"uid": "MET-OGE-PRAKT-TARIF", "title": "Задачи на тарифы и выбор",
             "description": "Сравнение тарифов, стоимостей. Выбор оптимального варианта. Процентные вычисления. ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-PRAKT-2", "title": "Выбор тарифа", "statement": "Тариф А: 300 руб + 2 руб/мин. Тариф Б: 5 руб/мин. При каком объёме А выгоднее?", "solution": "300+2x < 5x. 300 < 3x. x > 100. При >100 мин тариф А выгоднее.", "difficulty_level": 1}]},
            {"uid": "MET-OGE-PRAKT-MASSHTAB", "title": "Задачи с масштабом",
             "description": "Масштаб 1:1000 → 1 см на плане = 10 м в реальности. Перевод размеров, площадей (площадь ×масштаб²). ОГЭ 2026.",
             "examples": [{"uid": "EX-OGE-PRAKT-3", "title": "Масштаб", "statement": "На плане 1:500 длина участка 6 см. Реальная длина?", "solution": "6 · 500 = 3000 см = 30 м.", "difficulty_level": 1}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 9, "uc_max": 9, "methods": methods}])

    # ЕГЭ topics (11 кл)
    for uid, skl_uid, title, methods in [
        ("TOP-EGE-EKONOMICHESKIE-ZADACHI-2026", "SKL-EGE-EKON-SEED", "ЕГЭ: Экономические задачи", [
            {"uid": "MET-EGE-EKON-KREDIT", "title": "Задачи на кредиты",
             "description": "Аннуитетный: равные платежи. Дифференцированный: убывающие. Формула: S = P·rⁿ (простые проценты: S=P(1+rn)). ЕГЭ 2026, задание 17.",
             "examples": [{"uid": "EX-EGE-EKON-1", "title": "Кредит", "statement": "Кредит 100 000 под 10% годовых на 2 года (простые). Сколько вернуть?", "solution": "S = 100000(1+0.1·2) = 120 000 руб.", "difficulty_level": 2}]},
            {"uid": "MET-EGE-EKON-VKLAD", "title": "Задачи на вклады",
             "description": "Сложные проценты: S = P(1+r)ⁿ. Капитализация: ежемесячная, ежеквартальная. ЕГЭ 2026.",
             "examples": [{"uid": "EX-EGE-EKON-2", "title": "Вклад", "statement": "50 000 под 12% годовых, ежемесячная капитализация, 2 года.", "solution": "S = 50000(1+0.01)²⁴ = 50000·1.2697 ≈ 63 487 руб.", "difficulty_level": 2}]},
            {"uid": "MET-EGE-EKON-OPTIMIZ", "title": "Оптимизация в экономических задачах",
             "description": "Максимизация прибыли, минимизация затрат. Составляем функцию, находим экстремум (производная = 0 или ограниченная область). ЕГЭ 2026.",
             "examples": [{"uid": "EX-EGE-EKON-3", "title": "Максимум прибыли", "statement": "Прибыль P(x) = −x² + 100x − 400. Максимум?", "solution": "P'(x) = −2x+100 = 0. x = 50. P(50) = −2500+5000−400 = 2100.", "difficulty_level": 2}]},
        ]),
        ("TOP-EGE-FINANSOVAYA-MATEMATIKA-2026", "SKL-EGE-FINMAT-SEED", "ЕГЭ: Финансовая математика", [
            {"uid": "MET-EGE-FIN-ANNUITET", "title": "Аннуитетные платежи",
             "description": "A = S·r(1+r)ⁿ/((1+r)ⁿ−1). Равные ежемесячные платежи. Общая сумма выплат = A·n. Переплата = A·n − S. ЕГЭ 2026.",
             "examples": [{"uid": "EX-EGE-FIN-1", "title": "Аннуитет", "statement": "Кредит 1 000 000, 1% в месяц, 12 месяцев. Ежемесячный платёж?", "solution": "A = 1000000·0.01·1.01¹²/(1.01¹²−1) ≈ 88 849 руб.", "difficulty_level": 3}]},
        ]),
        ("TOP-EGE-PLANIMETRIYA-ZADACHI-2026", "SKL-EGE-PLANIM-SEED", "ЕГЭ: Планиметрия", [
            {"uid": "MET-EGE-PLAN-KOMBIN", "title": "Комбинированные задачи планиметрии",
             "description": "Сочетание теорем: Пифагор + подобие + вписанные углы. Многошаговое решение. ЕГЭ 2026, задание 16.",
             "examples": [{"uid": "EX-EGE-PLAN-1", "title": "Задача на вписанные фигуры", "statement": "В окружность вписан △ABC: AB=13, BC=14, AC=15. Найдите R.", "solution": "p = 21. S = √(21·8·7·6) = √7056 = 84. R = abc/(4S) = 13·14·15/(4·84) = 2730/336 = 65/8 = 8.125.", "difficulty_level": 3}]},
        ]),
        ("TOP-EGE-STEREOMETRIYA-ZADACHI-2026", "SKL-EGE-STER-SEED", "ЕГЭ: Стереометрия", [
            {"uid": "MET-EGE-STER-SECHENIE", "title": "Построение сечений и вычисление",
             "description": "Сечение — плоская фигура от пересечения плоскости с многогранником. Метод следов. Вычисление площади через координаты или теоремы. ЕГЭ 2026, задание 14.",
             "examples": [{"uid": "EX-EGE-STER-1", "title": "Сечение куба", "statement": "Куб ABCDA₁B₁C₁D₁, ребро 6. Сечение через A, C, B₁. Площадь?", "solution": "AC = 6√2, AB₁ = 6√2, CB₁ = 6√2. Равносторонний △ со стороной 6√2. S = (6√2)²√3/4 = 72√3/4 = 18√3.", "difficulty_level": 3}]},
        ]),
        ("TOP-EGE-TEORIYA-CHISEL-DELIMOST-2026", "SKL-EGE-TEORCH-SEED", "ЕГЭ: Теория чисел и делимость", [
            {"uid": "MET-EGE-TEORCH-ZADACHI", "title": "Задачи на делимость и остатки",
             "description": "Делимость, остатки, чётность, разложение на множители. Метод: анализ делимости, подбор с доказательством. ЕГЭ 2026, задание 19.",
             "examples": [{"uid": "EX-EGE-TEORCH-1", "title": "Делимость", "statement": "Докажите: n³−n делится на 6 для любого n∈ℤ.", "solution": "n³−n = n(n²−1) = (n−1)n(n+1) — произведение трёх последовательных. Среди них есть кратное 2 и кратное 3. Значит делится на 6.", "difficulty_level": 2}]},
        ]),
        ("TOP-EGE-ZADACHI-S-PARAMETROM-2026", "SKL-EGE-PARAM-SEED", "ЕГЭ: Задачи с параметром", [
            {"uid": "MET-EGE-PARAM-GRAFICH", "title": "Графический метод",
             "description": "Рассматриваем уравнение/неравенство на плоскости (x, a). Для каждого a определяем множество решений. Строим «динамический» график. ЕГЭ 2026, задание 18.",
             "examples": [{"uid": "EX-EGE-PARAM-1", "title": "Задача с параметром", "statement": "При каких a уравнение |x−1| = a имеет ровно 2 решения?", "solution": "y=|x−1| — V-образная, вершина (1;0). y=a — горизонталь. 2 решения при a > 0.", "difficulty_level": 2}]},
            {"uid": "MET-EGE-PARAM-ANALITICH", "title": "Аналитический метод",
             "description": "Рассмотрение случаев, дискриминант от параметра, ОДЗ от параметра. ЕГЭ 2026, задание 18.",
             "examples": [{"uid": "EX-EGE-PARAM-2", "title": "Дискриминант от параметра", "statement": "x² + 2ax + a + 2 = 0 имеет 2 корня. Найдите a.", "solution": "D = 4a²−4(a+2) > 0. a²−a−2 > 0. (a−2)(a+1) > 0. a < −1 или a > 2.", "difficulty_level": 2}]},
        ]),
    ]:
        ops += _build_ops_from_topic_def(uid, skl_uid, title,
            [{"uc_min": 11, "uc_max": 11, "methods": methods}])

    return ops


# ═══════════════════════════════════════════════════════════════════════════
# Proposal builder
# ═══════════════════════════════════════════════════════════════════════════

SECTION_BUILDERS: dict[str, callable] = {
    "arithmetic": _arithmetic_ops,
    "numbers": _numbers_structures_ops,
    "algebra": _algebra_ops,
    "functions": _functions_ops,
    "trigonometry": _trigonometry_ops,
    "geometry": _geometry_ops,
    "analytic_geometry": _analytic_geometry_ops,
    "analysis": _analysis_ops,
    "foundations": _foundations_ops,
    "linear_algebra": _linear_algebra_ops,
    "discrete_math": _discrete_math_ops,
    "probability": _probability_all_ops,
    "statistics": _statistics_ops,
    "exams": _exam_ops,
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
    parser.add_argument("--api-key", default=None, help="Admin API key for Bearer auth")
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

    client = httpx.Client(base_url=args.kb_url, timeout=60)
    headers: dict[str, str] = {"X-Tenant-ID": args.tenant_id}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"

    for i, payload in enumerate(proposals, 1):
        print(f"\n--- Submitting proposal {i}/{len(proposals)} ({len(payload['operations'])} ops)...")
        resp = client.post("/v1/proposals", json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"  ERROR create: {resp.status_code} {resp.text}", file=sys.stderr)
            continue
        data = resp.json()
        # Response may be {"proposal_id": ...} or {"items": [{"proposal_id": ...}]}
        proposal_id = data.get("proposal_id") or (data.get("items", [{}])[0].get("proposal_id") if data.get("items") else None)
        if not proposal_id:
            print(f"  ERROR: no proposal_id in response: {data}", file=sys.stderr)
            continue
        print(f"  Created: {proposal_id} (status={data.get('status', '?')})")

        commit_resp = client.post(f"/v1/proposals/{proposal_id}/commit", headers=headers)
        if commit_resp.status_code == 200:
            cd = commit_resp.json()
            ok = cd.get("ok") or (cd.get("items", [{}])[0].get("ok") if cd.get("items") else False)
            gv = cd.get("graph_version") or (cd.get("items", [{}])[0].get("graph_version") if cd.get("items") else None)
            if ok:
                print(f"  Committed! graph_version={gv}")
            else:
                print(f"  Commit failed: {cd}", file=sys.stderr)
        else:
            print(f"  ERROR commit: {commit_resp.status_code} {commit_resp.text}", file=sys.stderr)

    client.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
