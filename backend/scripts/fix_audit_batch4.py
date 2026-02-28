#!/usr/bin/env python3
"""Batch 4: Нормальное распр., Объёмы, Окружность, Описание данных (2 темы)."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 31. Нормальное распределение
    {
        "topic_uid": "TOP-NORMALNOE-RASPREDELENIE-ce0938",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-NORMAL-DISTR",
            "title": "Нормальное распределение",
            "definition": "Кривая Гаусса N(μ,σ²). Симметрична относительно μ. Основной закон статистики.",
            "methods": [
                {"uid": "MET-NORM-RULE3S", "title": "Правило трёх сигм",
                 "description": "P(μ−σ<X<μ+σ)≈68%, P(μ−2σ<X<μ+2σ)≈95%, P(μ−3σ<X<μ+3σ)≈99.7%.",
                 "examples": [{"uid": "EX-NORM-001", "title": "Правило 3σ", "statement": "IQ: μ=100, σ=15. Какой % людей имеет IQ от 70 до 130?", "solution": "70=100−2·15, 130=100+2·15. Это μ±2σ → ≈95%."}]},
                {"uid": "MET-NORM-ZSCORE", "title": "Z-оценка (стандартизация)",
                 "description": "Z = (X−μ)/σ. Переводит любое N(μ,σ²) в стандартное N(0,1). По таблицам Φ(z) находят вероятности.",
                 "examples": [{"uid": "EX-NORM-002", "title": "Z-оценка", "statement": "Рост: μ=170, σ=8. Какая доля выше 186?", "solution": "Z=(186−170)/8=2. P(Z>2)≈0.0228, т.е. ≈2.3%."}]},
                {"uid": "MET-NORM-APPLY", "title": "Применение нормального распределения",
                 "description": "Используется для оценки вероятностей в задачах: рост людей, результаты экзаменов, ошибки измерений.",
                 "examples": [{"uid": "EX-NORM-003", "title": "Задача на нормальное распределение", "statement": "Масса яблок: μ=150г, σ=20г. P(130<X<170)?", "solution": "Z₁=(130−150)/20=−1, Z₂=(170−150)/20=1. P(−1<Z<1)≈0.68=68%."}]},
            ],
        }],
    },

    # 32. Объёмы (стереометрия, 10-11 класс)
    {
        "topic_uid": "TOP-OBYOMY-d44ad9",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-VOLUMES",
            "title": "Вычисление объёмов геометрических тел",
            "definition": "Формулы объёмов: призма, пирамида, цилиндр, конус, шар.",
            "methods": [
                {"uid": "MET-VOL-PRISM-CYL", "title": "Объём призмы и цилиндра",
                 "description": "V_призмы = S_осн·h. V_цилиндра = πr²h.",
                 "examples": [{"uid": "EX-VOL-001", "title": "Объём цилиндра", "statement": "Цилиндр: r=3, h=10. V=?", "solution": "V = π·3²·10 = 90π ≈ 282.7."}]},
                {"uid": "MET-VOL-PYR-CONE", "title": "Объём пирамиды и конуса",
                 "description": "V_пирамиды = (1/3)S_осн·h. V_конуса = (1/3)πr²h.",
                 "examples": [{"uid": "EX-VOL-002", "title": "Объём конуса", "statement": "Конус: r=4, h=9. V=?", "solution": "V = (1/3)π·16·9 = 48π ≈ 150.8."}]},
                {"uid": "MET-VOL-SPHERE", "title": "Объём шара",
                 "description": "V = (4/3)πr³. Площадь поверхности S = 4πr².",
                 "examples": [{"uid": "EX-VOL-003", "title": "Объём шара", "statement": "Шар: r=6. V=?", "solution": "V = (4/3)π·216 = 288π ≈ 904.8."}]},
            ],
        }],
    },

    # 33. Окружность (7-9 класс, Атанасян)
    {
        "topic_uid": "TOP-OKRUZHNOST-926fe8",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-CIRCLE-GEOM",
            "title": "Окружность и её элементы",
            "definition": "Радиус, диаметр, хорда, дуга, касательная, секущая. Длина окружности и площадь круга.",
            "methods": [
                {"uid": "MET-CIRCLE-LENGTH", "title": "Длина окружности и площадь круга",
                 "description": "C = 2πr = πd. S = πr². Длина дуги: l = (α/360°)·2πr.",
                 "examples": [{"uid": "EX-CIRCLE-001", "title": "Длина и площадь", "statement": "r=7. Найдите C и S.", "solution": "C = 2π·7 = 14π ≈ 44. S = π·49 = 49π ≈ 153.9."}]},
                {"uid": "MET-CIRCLE-ANGLES", "title": "Углы, связанные с окружностью",
                 "description": "Центральный угол = дуга. Вписанный = дуга/2. Угол между хордами = (дуга₁+дуга₂)/2.",
                 "examples": [{"uid": "EX-CIRCLE-002", "title": "Вписанный угол", "statement": "Дуга AB = 100°. Найдите вписанный угол ACB.", "solution": "Вписанный = 100°/2 = 50°."}]},
                {"uid": "MET-CIRCLE-TANGENT", "title": "Свойства касательной",
                 "description": "Касательная ⊥ радиусу в точке касания. Два отрезка касательных из одной точки равны.",
                 "examples": [{"uid": "EX-CIRCLE-003", "title": "Касательная", "statement": "Из точки A проведена касательная AB=12 и секущая ACD, AC=8, CD=10. Проверьте: AB²=AC·AD.", "solution": "AB²=144. AC·AD=8·18=144. ✓ Верно (свойство секущей и касательной)."}]},
            ],
        }],
    },

    # 34. Описание данных: меры разброса
    {
        "topic_uid": "TOP-OPISANIE-DANNYH-MERY-RAZ-65807e",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-DATA-SPREAD",
            "title": "Описание данных: характеристики разброса",
            "definition": "Размах, межквартильный размах, дисперсия, стандартное отклонение для описания разброса данных.",
            "methods": [
                {"uid": "MET-DSPREAD-RANGE", "title": "Размах и межквартильный размах",
                 "description": "Размах = max−min. IQR = Q₃−Q₁. IQR устойчивее к выбросам.",
                 "examples": [{"uid": "EX-DSPREAD-001", "title": "Сравнение мер", "statement": "Данные: 5,7,8,9,10,12,50. Найдите размах и IQR.", "solution": "Размах=50−5=45. Q₁=7, Q₃=12, IQR=5. IQR не чувствителен к выбросу 50."}]},
                {"uid": "MET-DSPREAD-VAR", "title": "Дисперсия выборки",
                 "description": "D = Σ(xᵢ−x̄)²/n. Для выборочной (несмещённой): s² = Σ(xᵢ−x̄)²/(n−1).",
                 "examples": [{"uid": "EX-DSPREAD-002", "title": "Дисперсия", "statement": "Данные: 4, 6, 8. x̄=6. D=?", "solution": "D = [(4−6)²+(6−6)²+(8−6)²]/3 = (4+0+4)/3 = 8/3 ≈ 2.67."}]},
                {"uid": "MET-DSPREAD-COMPARE", "title": "Сравнение разброса двух выборок",
                 "description": "Сравнивайте σ или IQR двух наборов данных. Бо́льший σ → данные более разбросаны.",
                 "examples": [{"uid": "EX-DSPREAD-003", "title": "Сравнение", "statement": "Класс А: σ=2.5. Класс Б: σ=1.2. У кого однороднее оценки?", "solution": "У класса Б (σ меньше — оценки ближе к среднему)."}]},
            ],
        }],
    },

    # 35. Описание данных: меры центральной тенденции
    {
        "topic_uid": "TOP-OPISANIE-DANNYH-MERY-CEN-4cff59",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-DATA-CENTER",
            "title": "Описание данных: меры центра",
            "definition": "Среднее, медиана, мода — характеристики «типичного» значения в наборе данных.",
            "methods": [
                {"uid": "MET-DCENTER-MEAN", "title": "Среднее арифметическое выборки",
                 "description": "x̄ = Σxᵢ/n. Учитывает все значения. Чувствительно к выбросам.",
                 "examples": [{"uid": "EX-DCENTER-001", "title": "Среднее", "statement": "Баллы: 72, 85, 90, 68, 95. x̄=?", "solution": "x̄ = (72+85+90+68+95)/5 = 410/5 = 82."}]},
                {"uid": "MET-DCENTER-MEDIAN-MODE", "title": "Медиана и мода выборки",
                 "description": "Медиана: упорядочьте, возьмите средний элемент. Мода: наиболее частое значение.",
                 "examples": [{"uid": "EX-DCENTER-002", "title": "Когда использовать медиану", "statement": "Доходы: 20, 25, 30, 28, 500 тыс. Что лучше характеризует «типичный» доход?", "solution": "Медиана=28 (средний). Среднее=120.6 — завышено выбросом 500. Медиана точнее."}]},
                {"uid": "MET-DCENTER-CHOOSE", "title": "Выбор подходящей меры центральной тенденции",
                 "description": "Среднее — при симметричном распределении. Медиана — при выбросах или скошенности. Мода — для категориальных данных.",
                 "examples": [{"uid": "EX-DCENTER-003", "title": "Выбор меры", "statement": "Размеры обуви покупателей: 38, 39, 40, 40, 40, 41, 42. Какая мера самая полезная?", "solution": "Мода = 40 (самый частый размер). Для закупок обуви мода важнее среднего."}]},
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
    print(f"\n{'='*60}\nBatch 4 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
