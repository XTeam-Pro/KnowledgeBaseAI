#!/usr/bin/env python3
"""Batch 3: Многогранники, Многочлены, Моделирование СП, Монотонность, Непрерывные распределения."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 26. Многогранники (10–11 класс, стереометрия, Атанасян)
    {
        "topic_uid": "TOP-MNOGOGRANNIKI-dd928d",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-POLYHEDRA",
            "title": "Многогранники и их свойства",
            "definition": "Призмы, пирамиды, правильные многогранники. Элементы, формулы площадей и объёмов.",
            "methods": [
                {"uid": "MET-POLY-PRISM", "title": "Вычисление объёма и площади поверхности призмы",
                 "description": "V = S_осн · h. S_полн = 2·S_осн + S_бок. S_бок = P_осн · h (для прямой призмы).",
                 "examples": [{"uid": "EX-POLY-001", "title": "Объём прямой призмы", "statement": "Правильная треугольная призма, сторона основания 4, высота 6. Найдите V.", "solution": "S_осн = (√3/4)·4² = 4√3. V = 4√3·6 = 24√3."}]},
                {"uid": "MET-POLY-PYRAMID", "title": "Вычисление объёма и площади пирамиды",
                 "description": "V = (1/3)·S_осн·h. Апофема — высота боковой грани. S_бок = (1/2)·P_осн·a (апофема).",
                 "examples": [{"uid": "EX-POLY-002", "title": "Объём пирамиды", "statement": "Правильная четырёхугольная пирамида, сторона основания 6, высота 4. V=?", "solution": "S_осн = 6² = 36. V = (1/3)·36·4 = 48."}]},
                {"uid": "MET-POLY-EULER", "title": "Формула Эйлера для многогранников",
                 "description": "V − E + F = 2, где V — вершины, E — рёбра, F — грани. Применяйте для проверки корректности.",
                 "examples": [{"uid": "EX-POLY-003", "title": "Проверка по Эйлеру", "statement": "Куб: V=8, E=12, F=6. Проверьте формулу Эйлера.", "solution": "8 − 12 + 6 = 2. ✓ Верно."}]},
            ],
        }],
    },

    # 27. Многочлены (7–8 класс, Макарычев)
    {
        "topic_uid": "TOP-MNOGOCHLENY-0cd461",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-POLYNOMIALS",
            "title": "Действия с многочленами",
            "definition": "Сложение, вычитание, умножение многочленов. Разложение на множители.",
            "methods": [
                {"uid": "MET-POLY-OPS", "title": "Сложение, вычитание и умножение многочленов",
                 "description": "Сложение: приведите подобные. Умножение: каждый член одного × каждый член другого, затем приведите подобные.",
                 "examples": [{"uid": "EX-POLYNOM-001", "title": "Умножение многочленов", "statement": "(2x+3)(x²−x+1) = ?", "solution": "2x·x²−2x·x+2x·1+3·x²−3·x+3·1 = 2x³−2x²+2x+3x²−3x+3 = 2x³+x²−x+3."}]},
                {"uid": "MET-POLY-FACTOR-GCF", "title": "Разложение вынесением общего множителя",
                 "description": "Найдите НОД коэффициентов и наименьшую степень переменной. Вынесите за скобку.",
                 "examples": [{"uid": "EX-POLYNOM-002", "title": "Вынесение за скобку", "statement": "Разложите: 6x³ − 9x².", "solution": "НОД = 3x². 6x³−9x² = 3x²(2x−3)."}]},
                {"uid": "MET-POLY-FACTOR-FSU", "title": "Разложение по формулам сокращённого умножения",
                 "description": "a²−b² = (a−b)(a+b). a²±2ab+b² = (a±b)². a³±b³ = (a±b)(a²∓ab+b²).",
                 "examples": [{"uid": "EX-POLYNOM-003", "title": "Разность квадратов", "statement": "Разложите: 4x²−25.", "solution": "4x²−25 = (2x)²−5² = (2x−5)(2x+5)."}]},
            ],
        }],
    },

    # 28. Моделирование случайных процессов
    {
        "topic_uid": "TOP-MODELIROVANIE-SLUCHAINYH-ddc404",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-RANDOM-MODEL",
            "title": "Моделирование случайных процессов",
            "definition": "Использование случайных экспериментов и моделей для изучения вероятностных закономерностей.",
            "methods": [
                {"uid": "MET-RMOD-EXPERIMENT", "title": "Проведение случайного эксперимента",
                 "description": "Определите пространство элементарных исходов. Проведите серию опытов, фиксируйте результаты, вычислите частоты.",
                 "examples": [{"uid": "EX-RMOD-001", "title": "Серия бросков", "statement": "Бросьте кубик 60 раз. Ожидаемая частота каждого числа?", "solution": "Ожидаемая частота = 60/6 = 10 раз для каждого числа. Реальные отклонения — естественны."}]},
                {"uid": "MET-RMOD-SIMULATE", "title": "Имитационное моделирование с помощью таблицы случайных чисел",
                 "description": "Сопоставьте исходам диапазоны случайных чисел. Генерируйте числа и определяйте исходы.",
                 "examples": [{"uid": "EX-RMOD-002", "title": "Моделирование монеты", "statement": "Чётные цифры = орёл, нечётные = решка. Цифры: 3,8,1,6,4. Результат?", "solution": "3→Р, 8→О, 1→Р, 6→О, 4→О. Результат: 3 орла, 2 решки. Частота орла = 0.6."}]},
                {"uid": "MET-RMOD-COMPARE", "title": "Сравнение модели с теорией",
                 "description": "Сравните экспериментальные частоты с теоретическими вероятностями. При большом n они должны сближаться (ЗБЧ).",
                 "examples": [{"uid": "EX-RMOD-003", "title": "Проверка модели", "statement": "100 бросков монеты: 56 орлов. Согласуется ли с P=0.5?", "solution": "Частота = 0.56, отклонение от 0.5 = 0.06. Для n=100 это допустимо (σ ≈ 0.05). Модель не противоречит теории."}]},
            ],
        }],
    },

    # 29. Монотонность (10 класс, алгебра и начала анализа)
    {
        "topic_uid": "TOP-MONOTONNOST-dbe010",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-MONOTONICITY",
            "title": "Монотонность функции",
            "definition": "Возрастание и убывание функции. Определение через производную.",
            "methods": [
                {"uid": "MET-MONO-DEFINITION", "title": "Определение монотонности по определению",
                 "description": "f возрастает на (a,b), если для любых x₁<x₂ из (a,b): f(x₁)<f(x₂). Убывает — наоборот.",
                 "examples": [{"uid": "EX-MONO-001", "title": "Монотонность по определению", "statement": "f(x)=2x+1. Возрастает или убывает?", "solution": "Если x₁<x₂, то 2x₁+1 < 2x₂+1, т.е. f(x₁)<f(x₂). Возрастает на всей числовой прямой."}]},
                {"uid": "MET-MONO-DERIVATIVE", "title": "Определение монотонности через производную",
                 "description": "f'(x)>0 на интервале → f возрастает. f'(x)<0 → убывает. f'(x)=0 в точке → возможен экстремум.",
                 "examples": [{"uid": "EX-MONO-002", "title": "Через производную", "statement": "f(x) = x³−3x. Найдите промежутки монотонности.", "solution": "f'(x)=3x²−3=3(x−1)(x+1). f'>0 при x<−1 и x>1 (возрастает), f'<0 при −1<x<1 (убывает)."}]},
                {"uid": "MET-MONO-TABLE", "title": "Таблица знаков производной",
                 "description": "1) Найдите f'(x). 2) Решите f'(x)=0. 3) Составьте таблицу знаков f' на интервалах. 4) Определите промежутки возрастания/убывания.",
                 "examples": [{"uid": "EX-MONO-003", "title": "Таблица знаков", "statement": "f(x)=x⁴−8x². Составьте таблицу монотонности.", "solution": "f'=4x³−16x=4x(x²−4)=4x(x−2)(x+2). Корни: −2,0,2. Знаки: (−∞,−2):−, (−2,0):+, (0,2):−, (2,+∞):+. Убывает: (−∞,−2)∪(0,2). Возрастает: (−2,0)∪(2,+∞)."}]},
            ],
        }],
    },

    # 30. Непрерывные вероятностные распределения
    {
        "topic_uid": "TOP-NEPRERYVNYE-VEROYATNOSTN-236631",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-CONT-DISTR",
            "title": "Непрерывные вероятностные распределения",
            "definition": "Распределения непрерывных СВ: плотность вероятности, функция распределения, равномерное и нормальное распределения.",
            "methods": [
                {"uid": "MET-CONT-DENSITY", "title": "Плотность вероятности и её свойства",
                 "description": "f(x) ≥ 0, ∫f(x)dx = 1. P(a ≤ X ≤ b) = ∫ₐᵇ f(x)dx — площадь под кривой.",
                 "examples": [{"uid": "EX-CONT-001", "title": "Равномерное распределение", "statement": "X ~ U[0,5]. Найдите P(1≤X≤3).", "solution": "f(x)=1/5 на [0,5]. P(1≤X≤3) = (3−1)·(1/5) = 2/5 = 0.4."}]},
                {"uid": "MET-CONT-NORMAL", "title": "Нормальное распределение и правило 3σ",
                 "description": "N(μ,σ²): μ — среднее, σ — отклонение. 68% в μ±σ, 95% в μ±2σ, 99.7% в μ±3σ.",
                 "examples": [{"uid": "EX-CONT-002", "title": "Правило 3σ", "statement": "Рост мужчин: μ=175, σ=7. Какой % имеет рост от 161 до 189?", "solution": "161=175−2·7, 189=175+2·7. Это μ±2σ → ~95%."}]},
                {"uid": "MET-CONT-CDF", "title": "Функция распределения непрерывной СВ",
                 "description": "F(x) = P(X≤x) = ∫₋∞ˣ f(t)dt. F непрерывна, неубывает. P(a<X<b) = F(b)−F(a).",
                 "examples": [{"uid": "EX-CONT-003", "title": "CDF", "statement": "F(x)=0 при x<0, x² при 0≤x≤1, 1 при x>1. Найдите P(0.5<X<0.8).", "solution": "P = F(0.8)−F(0.5) = 0.64−0.25 = 0.39."}]},
            ],
        }],
    },
]

def _merge_node(session, label, uid, props):
    all_props = {"uid": uid, "type": label, "tenant_id": TENANT_ID, "lifecycle_status": "ACTIVE", "updated_at": NOW_MS, **props}
    session.run(f"MERGE (n:{label} {{uid: $uid, tenant_id: $tid}}) SET n += $props", uid=uid, tid=TENANT_ID, props=all_props)

def _merge_rel(session, from_uid, rel_type, to_uid):
    session.run(f"MATCH (a {{uid: $from_uid, tenant_id: $tid}}), (b {{uid: $to_uid, tenant_id: $tid}}) MERGE (a)-[:{rel_type}]->(b)", from_uid=from_uid, to_uid=to_uid, tid=TENANT_ID)

def _delete_all_skill_rels(session, topic_uid, dry_run):
    existing = session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[:REQUIRES_SKILL]->(sk:Skill) RETURN sk.uid AS uid, sk.title AS title", uid=topic_uid, tid=TENANT_ID).data()
    if not existing: return 0
    for s in existing: print(f"      🗑️  Удаляю: {topic_uid} → {s['uid']} ({s['title']})")
    if not dry_run:
        session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[r:REQUIRES_SKILL]->(sk:Skill) DELETE r", uid=topic_uid, tid=TENANT_ID)
    return len(existing)

def seed(dry_run=False):
    repo = Neo4jRepo()
    drv = repo.driver
    stats = {"topics": 0, "skills": 0, "methods": 0, "examples": 0, "rels": 0, "deleted_rels": 0}
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
                    stats["skills"] += 1; stats["rels"] += 1
                    for method in skill.get("methods", []):
                        method_uid = method["uid"]
                        method_props = {k: v for k, v in method.items() if k not in ("uid", "examples")}
                        print(f"    [Method] {method_uid}: {method.get('title', '')}")
                        if not dry_run:
                            _merge_node(session, "Method", method_uid, method_props)
                            _merge_rel(session, skill_uid, "HAS_METHOD", method_uid)
                        stats["methods"] += 1; stats["rels"] += 1
                        for ex in method.get("examples", []):
                            ex_props = {k: v for k, v in ex.items() if k != "uid"}
                            if not dry_run:
                                _merge_node(session, "Example", ex["uid"], ex_props)
                                _merge_rel(session, method_uid, "HAS_EXAMPLE", ex["uid"])
                            stats["examples"] += 1; stats["rels"] += 1
    finally:
        repo.close()
    mode = "(DRY RUN)" if dry_run else "(ПРИМЕНЕНО)"
    print(f"\n{'='*60}\nBatch 3 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
