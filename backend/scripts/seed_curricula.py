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
    # ОГЭ Математика 2026 — 25 заданий
    # Ч1 (1–19): краткий ответ, 1 балл; Ч2 (20–25): развёрнутый, до 2 баллов
    # Источник: КИМ ФИПИ 2026, спецификация МА-9 ОГЭ 2026_СПЕЦ
    # Структура не изменилась по сравнению с 2025 г.
    # ==================================================================
    {
        "code": "RU-OGE-MATH-2026",
        "title": "ОГЭ Математика 2026",
        "standard": "ОГЭ",
        "language": "ru",
        "status": "active",
        "nodes": [
            # --- Часть 1: краткий ответ (задания 1–19) ---
            # Задания 1–4: единый практикоориентированный блок (общий текст-условие)
            # Проверяют применение математики из всех разделов в реальной ситуации
            {"order": 1,  "uid": "TOP-OGE-PRAKTIKO-ORIENTIROVANNYE-ZADACHI-2026", "task": "1,2,3,4"},
            # Задание 5: статистика — чтение таблиц и диаграмм
            {"order": 2,  "uid": "TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026",        "task": "5"},
            # Задания 6–7: числа, действия, координатная прямая
            {"order": 3,  "uid": "TOP-MATH-NUMBERS-CALCULATIONS",                 "task": "6,7"},
            # Задание 8: алгебраические преобразования (формулы сокращённого умножения)
            {"order": 4,  "uid": "TOP-MATH-ALGEBRA-TRANSFORMS",                   "task": "8,12"},
            # Задание 9: линейные/квадратные уравнения, системы, линейные неравенства
            {"order": 5,  "uid": "TOP-MATH-EQUATIONS-SYSTEMS",                    "task": "9"},
            # Задание 10: вероятность (классическое определение)
            {"order": 6,  "uid": "TOP-MATH-PROBABILITY-STATISTICS",               "task": "10"},
            # Задание 11: функции — построение и чтение графиков
            {"order": 7,  "uid": "TOP-MATH-FUNCTIONS-GRAPHS",                     "task": "11"},
            # Задание 13: неравенства — дробно-рациональные, координатная прямая (выбор ответа)
            {"order": 8,  "uid": "TOP-MATH-INEQUALITIES",                         "task": "13"},
            # Задание 14: арифметическая и геометрическая прогрессии
            {"order": 9,  "uid": "TOP-MATH-PROGRESSIONS",                         "task": "14"},
            # Задание 15: планиметрия — теорема Пифагора, тригонометрия в прямоугольном треугольнике
            {"order": 10, "uid": "TOP-PERIMETR-I-PLOSHCHAD-003",                  "task": "15"},
            # Задание 16: вписанные/описанные окружности, углы
            {"order": 11, "uid": "TOP-OKRUZHNOST-926fe8",                         "task": "16"},
            # Задания 17–18: свойства трапеции, параллелограмма; площади, объём параллелепипеда
            {"order": 12, "uid": "TOP-MATH-PLANE-GEOMETRY",                       "task": "17,18"},
            # Задание 19: логика — истинные и ложные высказывания
            {"order": 13, "uid": "TOP-VYSKAZYVANIYA-efcd74",                      "task": "19"},
            # --- Часть 2: развёрнутый ответ (задания 20–25) ---
            # Задание 20: уравнения/системы (алгебра, в т.ч. нелинейные)
            {"order": 14, "uid": "TOP-MATH-ADVANCED-ALGEBRA",                     "task": "20"},
            # Задание 21: текстовая задача (составление уравнения/системы по условию)
            {"order": 15, "uid": "TOP-TEKSTOVYE-ZADACHI-004",                     "task": "21"},
            # Задание 22: функции с параметром — нахождение значений параметра
            {"order": 16, "uid": "TOP-MATH-ADVANCED-FUNCTIONS",                   "task": "22"},
            # Задание 23: вычислительная планиметрия (подобие, Пифагор, тригонометрия)
            {"order": 17, "uid": "TOP-MATH-PLANE-GEOMETRY",                       "task": "23"},
            # Задание 24: планиметрия с доказательством
            {"order": 18, "uid": "TOP-OGE-GEOMETRICHESKOE-DOKAZATELSTVO-2026",    "task": "24"},
            # Задание 25: сложная планиметрия (вписанные окружности, расстояния, площади)
            {"order": 19, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM",                  "task": "25"},
        ],
    },
    # ==================================================================
    # ЕГЭ Базовый Математика 2026 — 21 задание (все краткий ответ, базовый уровень)
    # Максимум 21 балл, время 3 часа
    # Источник: КИМ ФИПИ 2026, спецификация МА-11 ЕГЭ 2026 СПЕЦ_базовый
    # Структура не изменилась по сравнению с 2025 г.
    # ==================================================================
    {
        "code": "RU-EGE-BASE-MATH-2026",
        "title": "ЕГЭ Базовый Математика 2026",
        "standard": "ЕГЭ Базовый",
        "language": "ru",
        "status": "active",
        "nodes": [
            # Задание 1: вычисления — степени, корни, числовые выражения
            {"order": 1,  "uid": "TOP-MATH-NUMBERS-CALCULATIONS",                 "task": "1"},
            # Задание 2: текстовые задачи, оценка размеров объектов
            {"order": 2,  "uid": "TOP-TEKSTOVYE-ZADACHI-004",                     "task": "2"},
            # Задание 3: извлечение информации из таблиц, диаграмм, графиков
            {"order": 3,  "uid": "TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026",        "task": "3"},
            # Задание 4: вычисления и преобразования; текстовые задачи
            {"order": 4,  "uid": "TOP-MATH-ALGEBRA-TRANSFORMS",                   "task": "4"},
            # Задание 5: вероятность (простейшие случаи)
            {"order": 5,  "uid": "TOP-MATH-PROBABILITY-STATISTICS",               "task": "5"},
            # Задание 6: таблицы и диаграммы (более сложный уровень)
            {"order": 6,  "uid": "TOP-GRAFICHESKOE-PREDSTAVLEN-c2da9b",           "task": "6"},
            # Задание 7: функции — производная, описание поведения по графику
            {"order": 7,  "uid": "TOP-MATH-FUNCTIONS-GRAPHS",                     "task": "7"},
            # Задание 8: доказательные рассуждения, логика
            {"order": 8,  "uid": "TOP-VYSKAZYVANIYA-efcd74",                      "task": "8"},
            # Задания 9–10: теоремы планиметрии
            {"order": 9,  "uid": "TOP-MATH-PLANE-GEOMETRY",                       "task": "9,10,12"},
            # Задания 11, 13: стереометрия (объёмы, площади поверхностей)
            {"order": 10, "uid": "TOP-MATH-STEREOMETRY",                          "task": "11,13"},
            # Задания 14, 16: вычисления и преобразования выражений
            {"order": 11, "uid": "TOP-MATH-ALGEBRA-TRANSFORMS",                   "task": "14,16"},
            # Задание 15: вычисления; текстовые задачи
            {"order": 12, "uid": "TOP-MATH-NUMBERS-CALCULATIONS",                 "task": "15"},
            # Задание 17: уравнения — рациональные, иррациональные, показательные, тригонометрические, логарифмические
            {"order": 13, "uid": "TOP-MATH-EQUATIONS-SYSTEMS",                    "task": "17"},
            # Задание 18: неравенства — рациональные, показательные, логарифмические
            {"order": 14, "uid": "TOP-MATH-INEQUALITIES",                         "task": "18"},
            # Задание 19: финансово-экономические задачи (проценты, кредиты)
            {"order": 15, "uid": "TOP-EGE-FINANSOVAYA-MATEMATIKA-2026",           "task": "19"},
            # Задание 20: текстовые задачи (решение уравнений)
            {"order": 16, "uid": "TOP-TEKSTOVYE-ZADACHI-004",                     "task": "20"},
            # Задание 21: комплексная задача — вычисления, текстовые задачи, выбор метода
            {"order": 17, "uid": "TOP-MATH-ADVANCED-ALGEBRA",                     "task": "21"},
        ],
    },
    # ==================================================================
    # ЕГЭ Профиль Математика 2026 — 19 заданий
    # Ч1 (1–12): краткий ответ; Ч2 (13–19): развёрнутый ответ
    # Источник: КИМ ФИПИ 2026, спецификация МА-11 ЕГЭ 2026 СПЕЦ_профильный
    # Структура не изменилась по сравнению с 2025 г.
    # ==================================================================
    {
        "code": "RU-EGE-PROF-MATH-2026",
        "title": "ЕГЭ Профиль Математика 2026",
        "standard": "ЕГЭ Профиль",
        "language": "ru",
        "status": "active",
        "nodes": [
            # --- Часть 1: краткий ответ (задания 1–12, базовый/повышенный уровень) ---
            # Задание 1 (Б): планиметрия — площадь, длина, угол, подобие
            {"order": 1,  "uid": "TOP-MATH-PLANE-GEOMETRY",                       "task": "1"},
            # Задание 2 (Б): векторы — координаты, сумма, скалярное произведение, угол
            {"order": 2,  "uid": "TOP-VEKTORY-78d40c",                            "task": "2"},
            # Задание 3 (Б): стереометрия — двугранный угол, расстояния, объём
            {"order": 3,  "uid": "TOP-MATH-STEREOMETRY",                          "task": "3"},
            # Задание 4 (Б): теория вероятностей базовая — классическая вероятность
            {"order": 4,  "uid": "TOP-MATH-PROBABILITY-STATISTICS",               "task": "4"},
            # Задание 5 (П): теория вероятностей — формулы сложения/умножения, комбинаторика, геом. вероятность
            {"order": 5,  "uid": "TOP-MATH-COMBINATORICS",                        "task": "5"},
            # Задание 6 (Б): уравнения и неравенства — линейные, квадратные, простые системы
            {"order": 6,  "uid": "TOP-MATH-EQUATIONS-SYSTEMS",                    "task": "6"},
            # Задание 7 (Б): степени и логарифмы — вычисления и преобразования выражений
            # (НЕ уравнения! Упрощение, вычисление значений: a^(log_a b), √, дробно-рациональные)
            {"order": 7,  "uid": "TOP-MATH-EXP-LOG",                              "task": "7"},
            # Задание 8 (Б): производная и интеграл — экстремум, наиб/наим значение, касательная, площадь
            {"order": 8,  "uid": "TOP-MATH-DERIVATIVES",                          "task": "8"},
            # Задание 9 (П): математическое моделирование — составление уравнений/систем по условию
            {"order": 9,  "uid": "TOP-MATH-APPLIED-MATH",                         "task": "9"},
            # Задание 10 (П): текстовые задачи — смеси, работа, движение, оценка правдоподобности
            {"order": 10, "uid": "TOP-TEKSTOVYE-ZADACHI-004",                     "task": "10"},
            # Задание 11 (П): свойства и графики функций — решение уравнений через графики и свойства
            {"order": 11, "uid": "TOP-MATH-FUNCTIONS-GRAPHS",                     "task": "11"},
            # Задание 12 (П): исследование функции через производную — экстремумы, монотонность
            {"order": 12, "uid": "TOP-MATH-CALCULUS",                             "task": "12"},
            # --- Часть 2: развёрнутый ответ (задания 13–19) ---
            # Задание 13 (П, 2 балла): тригонометрические уравнения с отбором корней на промежутке
            {"order": 13, "uid": "TOP-MATH-ADVANCED-TRIG",                        "task": "13"},
            # Задание 14 (П, 3 балла): стереометрия с доказательством — двугранные углы, расстояния, сечения
            {"order": 14, "uid": "TOP-MATH-STEREOMETRY-ADVANCED",                 "task": "14"},
            # Задание 15 (П, 2 балла): показательные и логарифмические уравнения/неравенства
            {"order": 15, "uid": "TOP-MATH-COMPLEX-INEQUALITIES",                 "task": "15"},
            # Задание 16 (П, 2 балла): финансово-экономические задачи — кредиты, проценты, личные финансы
            {"order": 16, "uid": "TOP-MATH-FINANCIAL-ADVANCED",                   "task": "16"},
            # Задание 17 (П, 3 балла): планиметрия с доказательством — вписанные/описанные фигуры
            {"order": 17, "uid": "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF",            "task": "17"},
            # Задание 18 (В, 4 балла): задачи с параметром — системы/неравенства, свойства функций
            {"order": 18, "uid": "TOP-EGE-ZADACHI-S-PARAMETROM-2026",             "task": "18"},
            # Задание 19 (В, 4 балла): теория чисел/комбинаторика — делимость, НОД/НОК, чётность
            {"order": 19, "uid": "TOP-EGE-TEORIYA-CHISEL-DELIMOST-2026",          "task": "19"},
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
