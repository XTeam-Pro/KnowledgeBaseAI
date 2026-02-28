#!/usr/bin/env python3
"""Batch 8: Последние 10 критических тем (61–70)."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 61. Стереометрия: объёмы и площади (нужно добавить 1 метод)
    {"topic_uid": "TOP-MATH-STEREOMETRY", "remove_all_old_skills": False, "skills": [{
        "uid": "SKL-STEREO-VOL-AREA", "title": "Формулы объёмов и площадей поверхностей",
        "definition": "Систематизация формул для призм, пирамид, цилиндров, конусов и шара.",
        "methods": [
            {"uid": "MET-STV-ROTATION", "title": "Объём и площадь тел вращения",
             "description": "Цилиндр: V=πr²h, S=2πr(r+h). Конус: V=(1/3)πr²h, S=πr(r+l). Шар: V=(4/3)πr³, S=4πr².",
             "examples": [{"uid": "EX-STV-001", "title": "Полная поверхность конуса", "statement": "Конус: r=3, l=5. Sполн?", "solution": "Sполн = πr(r+l) = π·3·(3+5) = 24π."}]},
            {"uid": "MET-STV-COMPOSITE", "title": "Объём составных тел",
             "description": "Разбейте тело на простые (цилиндр + конус, призма − пирамида). Сложите или вычтите объёмы.",
             "examples": [{"uid": "EX-STV-002", "title": "Составное тело", "statement": "Цилиндр r=2, h=5 с конусом r=2, h=3 сверху. V=?", "solution": "V = π·4·5 + (1/3)π·4·3 = 20π + 4π = 24π."}]},
        ],
    }]},

    # 62. Стереометрия: расстояния и углы (нужно добавить 1 метод)
    {"topic_uid": "TOP-MATH-STEREOMETRY-ADVANCED", "remove_all_old_skills": False, "skills": [{
        "uid": "SKL-STEREO-ADV", "title": "Расстояния и углы в пространстве",
        "definition": "Расстояние между скрещивающимися прямыми, угол между прямой и плоскостью, двугранные углы.",
        "methods": [
            {"uid": "MET-STADV-DIHEDRAL", "title": "Нахождение двугранного угла",
             "description": "Двугранный угол — угол между полуплоскостями. Найдите его через перпендикуляры к ребру из точки ребра.",
             "examples": [{"uid": "EX-STADV-001", "title": "Двугранный угол", "statement": "Куб, ребро 1. Двугранный угол при ребре AB грани ABCD и сечения ABD₁?", "solution": "Перпендикуляры из середины AB: в грани ABCD и в сечении. tg α = 1/(0.5) → α = arctan 2 ≈ 63.4°."}]},
        ],
    }]},

    # 63. Таблица умножения (2–3 класс, Моро/Виленкин)
    {"topic_uid": "TOPIC-MULT-TABLE", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-MULT-TABLE-FIX", "title": "Таблица умножения",
        "definition": "Таблица умножения однозначных чисел от 2×2 до 9×9. Основа быстрого счёта.",
        "methods": [
            {"uid": "MET-MT-GROUPS", "title": "Изучение по столбцам (таблицы)",
             "description": "Учите по одному множителю: ×2 (2,4,6,...), ×3 (3,6,9,...) и т.д. Проверяйте каждую таблицу.",
             "examples": [{"uid": "EX-MT-001", "title": "Таблица на 7", "statement": "Заполните: 7×3=?, 7×6=?, 7×8=?.", "solution": "7×3=21, 7×6=42, 7×8=56."}]},
            {"uid": "MET-MT-COMMUTATIVE", "title": "Переместительный закон умножения",
             "description": "a×b = b×a. Если не помните 3×7, вспомните 7×3=21. Это сокращает объём запоминания вдвое.",
             "examples": [{"uid": "EX-MT-002", "title": "Перестановка", "statement": "Вычислите 4×9, используя 9×4.", "solution": "9×4 = 36. Значит 4×9 = 36."}]},
            {"uid": "MET-MT-TRICKS", "title": "Приёмы быстрого умножения",
             "description": "×9: умножьте на 10 и вычтите число (7×9=70−7=63). ×5: разделите на 2 и умножьте на 10 (8×5=80/2=40→нет, 8×5=40).",
             "examples": [{"uid": "EX-MT-003", "title": "Умножение на 9", "statement": "6×9 = ?", "solution": "6×10 − 6 = 60 − 6 = 54. Или: десятки = 6−1=5, единицы = 9−5=4 → 54."}]},
        ],
    }]},

    # 64. Тестирование гипотез с использованием распределений
    {"topic_uid": "TOP-TESTIROVANIE-GIPOTEZ-S-I-83526e", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-HYP-DISTR", "title": "Проверка гипотез с использованием распределений",
        "definition": "Применение нормального, t-распределения Стьюдента и χ² для проверки гипотез.",
        "methods": [
            {"uid": "MET-HYPD-ZTEST", "title": "Z-критерий для проверки среднего",
             "description": "Z = (x̄−μ₀)/(σ/√n). Если |Z| > z_крит — отвергаем H₀. Для 95%: z_крит = 1.96.",
             "examples": [{"uid": "EX-HYPD-001", "title": "Z-тест", "statement": "H₀: μ=100. x̄=104, σ=10, n=25. Отвергаем (α=0.05)?", "solution": "Z=(104−100)/(10/5)=4/2=2. |Z|=2 > 1.96 → отвергаем H₀."}]},
            {"uid": "MET-HYPD-TTEST", "title": "t-критерий Стьюдента",
             "description": "t = (x̄−μ₀)/(s/√n). Используется при неизвестном σ и малых n. Число степеней свободы: df = n−1.",
             "examples": [{"uid": "EX-HYPD-002", "title": "t-тест", "statement": "n=10, x̄=5.2, s=1.5, μ₀=4.5. t=?", "solution": "t = (5.2−4.5)/(1.5/√10) = 0.7/0.474 = 1.48. df=9. t_крит(0.05,9)≈2.26. 1.48<2.26 → не отвергаем H₀."}]},
            {"uid": "MET-HYPD-CHI2", "title": "Критерий хи-квадрат",
             "description": "χ² = Σ(Oᵢ−Eᵢ)²/Eᵢ. O — наблюдаемые частоты, E — ожидаемые. Проверяет согласие распределения с теоретическим.",
             "examples": [{"uid": "EX-HYPD-003", "title": "χ²-тест", "statement": "Кубик 60 бросков: 1→12, 2→8, 3→10, 4→9, 5→11, 6→10. Честный?", "solution": "E=10 для каждого. χ²=(4+4+0+1+1+0)/10=1.0. df=5. χ²_крит(0.05,5)=11.07. 1.0<11.07 → не отвергаем H₀ (кубик честный)."}]},
        ],
    }]},

    # 65. Типы данных и уровни измерений
    {"topic_uid": "TOP-TIPY-DANNYH-I-UROVNI-IZM-c9a86a", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-DATA-TYPES", "title": "Типы данных и шкалы измерений",
        "definition": "Номинальная, порядковая, интервальная, относительная шкалы. Качественные и количественные данные.",
        "methods": [
            {"uid": "MET-DT-SCALES", "title": "Четыре шкалы измерений",
             "description": "Номинальная: категории (пол, цвет). Порядковая: ранги (оценки). Интервальная: равные промежутки (температура °C). Относительная: есть нуль (рост, вес).",
             "examples": [{"uid": "EX-DT-001", "title": "Определение шкалы", "statement": "Температура тела: 36.6°C. Какая шкала?", "solution": "Интервальная: 0°C не означает «отсутствие температуры», но разности имеют смысл."}]},
            {"uid": "MET-DT-CLASSIFY", "title": "Классификация данных",
             "description": "Качественные (категориальные) vs количественные (числовые). Дискретные (целые) vs непрерывные (вещественные).",
             "examples": [{"uid": "EX-DT-002", "title": "Классификация", "statement": "Группа крови, рост, число детей, город проживания — какие типы?", "solution": "Группа крови — качеств. (номинальн.). Рост — количеств., непрер. Число детей — количеств., дискрет. Город — качеств. (номинальн.)."}]},
            {"uid": "MET-DT-CHOOSE-STAT", "title": "Выбор статистического метода по типу данных",
             "description": "Номинальные: мода, χ². Порядковые: медиана, ранговая корреляция. Интервальные/относительные: среднее, σ, t-тест.",
             "examples": [{"uid": "EX-DT-003", "title": "Выбор метода", "statement": "Данные: оценки (5,4,3,5,4). Какие характеристики уместны?", "solution": "Порядковая шкала → медиана=4, мода=4 и 5. Среднее (4.2) тоже допустимо, но медиана предпочтительнее."}]},
        ],
    }]},

    # 66. Финансово-экономические расчёты (нужно добавить 1 метод)
    {"topic_uid": "TOP-MATH-FINANCIAL-ADVANCED", "remove_all_old_skills": False, "skills": [{
        "uid": "SKL-FIN-ADV", "title": "Финансово-экономические расчёты",
        "definition": "Аннуитетные платежи, NPV, сравнение вариантов инвестирования.",
        "methods": [
            {"uid": "MET-FIN-ANNUITY", "title": "Вычисление аннуитетного платежа",
             "description": "A = S·r(1+r)ⁿ/((1+r)ⁿ−1), где S — сумма кредита, r — месячная ставка, n — число месяцев.",
             "examples": [{"uid": "EX-FIN-001", "title": "Аннуитет", "statement": "Кредит 100000 руб, 12% годовых, 12 месяцев. Ежемесячный платёж?", "solution": "r=0.01. A=100000·0.01·1.01¹²/(1.01¹²−1)=100000·0.01·1.1268/0.1268≈8885 руб."}]},
        ],
    }]},

    # 67. Функции: задачи повышенного уровня (нужно добавить 1 метод)
    {"topic_uid": "TOP-MATH-ADVANCED-FUNCTIONS", "remove_all_old_skills": False, "skills": [{
        "uid": "SKL-ADV-FUNC", "title": "Функции: задачи повышенного уровня",
        "definition": "Графический метод, задачи с параметром, исследование функций.",
        "methods": [
            {"uid": "MET-AFUNC-PARAM", "title": "Задачи с параметром: метод «подвижной прямой»",
             "description": "Постройте график функции. Параметр — горизонтальная/вертикальная прямая. Число пересечений = число решений.",
             "examples": [{"uid": "EX-AFUNC-001", "title": "Число решений", "statement": "x²=a. При каких a ровно 2 решения?", "solution": "y=x² — парабола. y=a — горизонтальная прямая. 2 пересечения при a>0."}]},
        ],
    }]},

    # 68. Центральная предельная теорема
    {"topic_uid": "TOP-CENTRALNAYA-PREDELNAYA-T-b48f16", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-CLT", "title": "Центральная предельная теорема",
        "definition": "Сумма большого числа независимых СВ имеет приближённо нормальное распределение, независимо от распределения слагаемых.",
        "methods": [
            {"uid": "MET-CLT-STATE", "title": "Формулировка ЦПТ",
             "description": "Если X₁,...,Xₙ — независимые одинаково распределённые СВ с E=μ, D=σ², то при n→∞: (x̄−μ)/(σ/√n) → N(0,1).",
             "examples": [{"uid": "EX-CLT-001", "title": "ЦПТ", "statement": "Среднее 100 бросков кубика. Каково распределение?", "solution": "E=3.5, σ²=35/12. По ЦПТ: x̄ ≈ N(3.5, 35/1200). σ_x̄ ≈ 0.17."}]},
            {"uid": "MET-CLT-APPLY", "title": "Применение ЦПТ для приближённых вычислений",
             "description": "Используйте нормальное приближение для суммы/среднего: P(a < x̄ < b) ≈ Φ((b−μ)/(σ/√n)) − Φ((a−μ)/(σ/√n)).",
             "examples": [{"uid": "EX-CLT-002", "title": "Приближение", "statement": "n=64, μ=50, σ=8. P(48 < x̄ < 52)?", "solution": "σ_x̄ = 8/8 = 1. P = Φ(2)−Φ(−2) ≈ 0.9544."}]},
            {"uid": "MET-CLT-WHEN", "title": "Когда можно применять ЦПТ",
             "description": "Обычно n ≥ 30 достаточно. Для сильно скошенных распределений нужно больше. Данные должны быть независимы.",
             "examples": [{"uid": "EX-CLT-003", "title": "Применимость", "statement": "n=10 из экспоненциального распределения. Можно ЦПТ?", "solution": "n=10 мало для скошенного распределения. Лучше n≥50. Для n=10 — нет."}]},
        ],
    }]},

    # 69. Числа и практические вычисления (нужно добавить 1 метод)
    {"topic_uid": "TOP-MATH-NUMBERS-CALCULATIONS", "remove_all_old_skills": False, "skills": [{
        "uid": "SKL-NUM-CALC", "title": "Практические вычисления с числами",
        "definition": "Проценты, пропорции, степени и корни на базовом уровне.",
        "methods": [
            {"uid": "MET-NCALC-PERCENT", "title": "Вычисление процентов",
             "description": "a% от b = a·b/100. Процентное изменение = (новое−старое)/старое · 100%.",
             "examples": [{"uid": "EX-NCALC-001", "title": "Процент", "statement": "Цена 2000 руб, скидка 15%. Итоговая цена?", "solution": "Скидка = 2000·15/100 = 300. Итого = 2000−300 = 1700 руб."}]},
            {"uid": "MET-NCALC-PROPORTION", "title": "Решение задач на пропорцию",
             "description": "a/b = c/d. Крест-накрест: a·d = b·c. Выразите неизвестное.",
             "examples": [{"uid": "EX-NCALC-002", "title": "Пропорция", "statement": "3 кг яблок стоят 240 руб. Сколько стоят 5 кг?", "solution": "3/240 = 5/x → x = 240·5/3 = 400 руб."}]},
        ],
    }]},

    # 70. Экспоненциальное распределение
    {"topic_uid": "TOP-EKSPONENCIALNOE-RASPREDE-a30410", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-EXPONENTIAL", "title": "Экспоненциальное распределение",
        "definition": "Модель времени ожидания. f(x) = λe⁻λˣ при x≥0. E(X) = 1/λ, D(X) = 1/λ².",
        "methods": [
            {"uid": "MET-EXP-FORMULA", "title": "Формулы экспоненциального распределения",
             "description": "f(x)=λe⁻λˣ, F(x)=1−e⁻λˣ. P(X>t) = e⁻λᵗ. E(X)=1/λ.",
             "examples": [{"uid": "EX-EXP-001", "title": "Время ожидания", "statement": "Клиенты приходят с λ=3 чел/час. P(ожидание > 30 мин)?", "solution": "P(X>0.5) = e⁻³·⁰·⁵ = e⁻¹·⁵ ≈ 0.223."}]},
            {"uid": "MET-EXP-MEMORYLESS", "title": "Свойство отсутствия памяти",
             "description": "P(X>s+t | X>s) = P(X>t). «Прошлое не влияет на будущее» — если уже ждали s, вероятность ждать ещё t та же.",
             "examples": [{"uid": "EX-EXP-002", "title": "Без памяти", "statement": "Лампочка работает в среднем 1000 ч. Уже проработала 500 ч. Средний оставшийся срок?", "solution": "По свойству без памяти: средний оставшийся срок = 1000 ч (как у новой)."}]},
            {"uid": "MET-EXP-APPLY", "title": "Применение экспоненциального распределения",
             "description": "Время между событиями в пуассоновском потоке. Время до отказа оборудования. Время обслуживания.",
             "examples": [{"uid": "EX-EXP-003", "title": "Надёжность", "statement": "Среднее время безотказной работы = 500 ч. P(откажет за первые 100 ч)?", "solution": "λ=1/500. P(X<100)=1−e⁻¹⁰⁰/⁵⁰⁰=1−e⁻⁰·²≈1−0.819=0.181≈18%."}]},
        ],
    }]},
]

def _merge_node(session, label, uid, props):
    all_props = {"uid": uid, "type": label, "tenant_id": TENANT_ID, "lifecycle_status": "ACTIVE", "updated_at": NOW_MS, **props}
    session.run(f"MERGE (n:{label} {{uid: $uid, tenant_id: $tid}}) SET n += $props", uid=uid, tid=TENANT_ID, props=all_props)

def _merge_rel(session, from_uid, rel_type, to_uid):
    session.run(f"MATCH (a {{uid: $from_uid, tenant_id: $tid}}), (b {{uid: $to_uid, tenant_id: $tid}}) MERGE (a)-[:{rel_type}]->(b)", from_uid=from_uid, to_uid=to_uid, tid=TENANT_ID)

def _delete_all_skill_rels(session, topic_uid, dry_run):
    existing = session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[:REQUIRES_SKILL]->(sk:Skill) RETURN sk.uid AS uid, sk.title AS title", uid=topic_uid, tid=TENANT_ID).data()
    if not existing: return 0
    for s in existing: print(f"      🗑️  {topic_uid} → {s['uid']} ({s['title']})")
    if not dry_run:
        session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[r:REQUIRES_SKILL]->(sk:Skill) DELETE r", uid=topic_uid, tid=TENANT_ID)
    return len(existing)

def seed(dry_run=False):
    repo = Neo4jRepo(); drv = repo.driver
    stats = {"topics": 0, "skills": 0, "methods": 0, "examples": 0, "deleted_rels": 0}
    try:
        with drv.session() as session:
            for entry in DATA:
                topic_uid = entry["topic_uid"]
                print(f"\n[Topic] {topic_uid}")
                if entry.get("remove_all_old_skills"):
                    stats["deleted_rels"] += _delete_all_skill_rels(session, topic_uid, dry_run)
                stats["topics"] += 1
                for skill in entry.get("skills", []):
                    skill_uid = skill["uid"]
                    skill_props = {k: v for k, v in skill.items() if k not in ("uid", "methods")}
                    print(f"  [Skill] {skill_uid}: {skill.get('title', '')}")
                    if not dry_run:
                        _merge_node(session, "Skill", skill_uid, skill_props)
                        _merge_rel(session, topic_uid, "REQUIRES_SKILL", skill_uid)
                    stats["skills"] += 1
                    for method in skill.get("methods", []):
                        method_uid = method["uid"]
                        method_props = {k: v for k, v in method.items() if k not in ("uid", "examples")}
                        print(f"    [Method] {method_uid}: {method.get('title', '')}")
                        if not dry_run:
                            _merge_node(session, "Method", method_uid, method_props)
                            _merge_rel(session, skill_uid, "HAS_METHOD", method_uid)
                        stats["methods"] += 1
                        for ex in method.get("examples", []):
                            if not dry_run:
                                _merge_node(session, "Example", ex["uid"], {k: v for k, v in ex.items() if k != "uid"})
                                _merge_rel(session, method_uid, "HAS_EXAMPLE", ex["uid"])
                            stats["examples"] += 1
    finally:
        repo.close()
    mode = "(DRY RUN)" if dry_run else "(ПРИМЕНЕНО)"
    print(f"\n{'='*60}\nBatch 8 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
