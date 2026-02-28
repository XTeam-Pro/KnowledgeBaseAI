#!/usr/bin/env python3
"""
Batch 2: Критические темы 21–25 (статистика, корреляция, математическое ожидание).
"""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 21. Корреляционный анализ
    {
        "topic_uid": "TOP-KORRELYACIONNYI-ANALIZ-d5a590",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-CORR-ANALYSIS",
            "title": "Корреляционный анализ данных",
            "definition": "Изучение линейной зависимости между двумя количественными переменными.",
            "methods": [
                {"uid": "MET-CORR-SCATTER", "title": "Построение диаграммы рассеяния",
                 "description": "Нанесите точки (xᵢ, yᵢ) на координатную плоскость. Если облако вытянуто — есть корреляция.",
                 "examples": [{"uid": "EX-CORR-001", "title": "Диаграмма рост-вес", "statement": "Рост: 160,165,170,175,180. Вес: 55,60,65,68,75. Постройте диаграмму рассеяния.", "solution": "Точки (160,55),(165,60),(170,65),(175,68),(180,75) — облако вытянуто вправо-вверх → положительная корреляция."}],
                },
                {"uid": "MET-CORR-COEFF", "title": "Вычисление коэффициента корреляции",
                 "description": "r = Σ(xᵢ−x̄)(yᵢ−ȳ) / √[Σ(xᵢ−x̄)²·Σ(yᵢ−ȳ)²]. |r| близок к 1 → сильная связь, к 0 → слабая.",
                 "examples": [{"uid": "EX-CORR-002", "title": "Расчёт r", "statement": "X: 1,2,3. Y: 2,4,5. Найдите r.", "solution": "x̄=2, ȳ=11/3≈3.67. Σ(xᵢ−x̄)(yᵢ−ȳ)=(−1)(−1.67)+(0)(0.33)+(1)(1.33)=1.67+0+1.33=3. Σ(xᵢ−x̄)²=2. Σ(yᵢ−ȳ)²=4.67. r=3/√(2·4.67)=3/3.06≈0.98."}],
                },
                {"uid": "MET-CORR-INTERPRET", "title": "Интерпретация коэффициента корреляции",
                 "description": "r>0 — прямая зависимость, r<0 — обратная. |r|>0.7 — сильная, 0.3<|r|<0.7 — средняя, |r|<0.3 — слабая. Корреляция ≠ причинность!",
                 "examples": [{"uid": "EX-CORR-003", "title": "Интерпретация", "statement": "r = −0.85. Что это значит?", "solution": "Сильная обратная зависимость: при увеличении X значение Y уменьшается. Но это не обязательно означает причинно-следственную связь."}],
                },
            ],
        }],
    },

    # 22. Коэффициенты асимметрии и эксцесса
    {
        "topic_uid": "TOP-KOEFFICIENTY-ASIMMETRII--55d6ee",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-SKEW-KURT",
            "title": "Коэффициенты асимметрии и эксцесса",
            "definition": "Характеристики формы распределения: асимметрия — скошенность, эксцесс — островершинность.",
            "methods": [
                {"uid": "MET-SKEW-CALC", "title": "Вычисление коэффициента асимметрии",
                 "description": "As = (x̄ − Mo) / σ (формула Пирсона). As>0 — правосторонняя, As<0 — левосторонняя, As≈0 — симметричное.",
                 "examples": [{"uid": "EX-SKEW-001", "title": "Асимметрия", "statement": "x̄=52, Mo=48, σ=10. Найдите As.", "solution": "As = (52−48)/10 = 0.4 > 0 — правосторонняя асимметрия (хвост вправо)."}],
                },
                {"uid": "MET-SKEW-VISUAL", "title": "Определение асимметрии по гистограмме",
                 "description": "Сравните положение среднего и медианы. x̄ > Me — правая асимметрия. x̄ < Me — левая.",
                 "examples": [{"uid": "EX-SKEW-002", "title": "Асимметрия по графику", "statement": "Гистограмма зарплат: длинный хвост вправо. Какая асимметрия?", "solution": "Правосторонняя (положительная). Среднее > медианы из-за высоких зарплат."}],
                },
                {"uid": "MET-KURT-CALC", "title": "Вычисление эксцесса",
                 "description": "Ex = [Σ(xᵢ−x̄)⁴ / (n·σ⁴)] − 3. Ex>0 — островершинное, Ex<0 — плосковершинное, Ex≈0 — нормальное.",
                 "examples": [{"uid": "EX-KURT-001", "title": "Эксцесс", "statement": "Данные сильно сконцентрированы вокруг среднего с редкими выбросами. Какой эксцесс?", "solution": "Положительный (Ex > 0) — островершинное распределение (лептокуртическое)."}],
                },
            ],
        }],
    },

    # 23. Математическое ожидание
    {
        "topic_uid": "TOP-MATEMATICHESKOE-OZHIDANI-d5d8c8",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EXPECTED-VALUE",
            "title": "Математическое ожидание случайной величины",
            "definition": "E(X) — среднее значение СВ при большом числе опытов. Взвешенное среднее значений по вероятностям.",
            "methods": [
                {"uid": "MET-EV-DISCRETE", "title": "Вычисление E(X) для дискретной СВ",
                 "description": "E(X) = Σ xᵢ · P(xᵢ). Умножьте каждое значение на его вероятность и сложите.",
                 "examples": [{"uid": "EX-EV-001", "title": "Ожидание выигрыша", "statement": "Выигрыш: 100 руб с P=0.3, 0 руб с P=0.5, −50 руб с P=0.2. Найдите E(X).", "solution": "E(X) = 100·0.3 + 0·0.5 + (−50)·0.2 = 30 + 0 − 10 = 20 руб."}],
                },
                {"uid": "MET-EV-PROPERTIES", "title": "Свойства математического ожидания",
                 "description": "E(aX+b) = aE(X)+b. E(X+Y) = E(X)+E(Y) (всегда). E(XY) = E(X)E(Y) только для независимых.",
                 "examples": [{"uid": "EX-EV-002", "title": "Линейность E", "statement": "E(X)=5. Найдите E(3X+2).", "solution": "E(3X+2) = 3·E(X) + 2 = 3·5 + 2 = 17."}],
                },
                {"uid": "MET-EV-FAIR", "title": "Применение E(X) для оценки справедливости игры",
                 "description": "Игра справедлива, если E(выигрыша) = 0. Если E > 0 — выгодно игроку, E < 0 — выгодно казино.",
                 "examples": [{"uid": "EX-EV-003", "title": "Справедливость игры", "statement": "Ставка 10 руб. Выигрыш 50 с P=0.15, проигрыш с P=0.85. Справедлива ли игра?", "solution": "E = 50·0.15 + (−10)·0.85 = 7.5 − 8.5 = −1. E < 0 → игра не в пользу игрока."}],
                },
            ],
        }],
    },

    # 24. Меры разброса
    {
        "topic_uid": "TOP-MERY-RAZBROSA-c487ac",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-SPREAD-MEASURES",
            "title": "Меры разброса данных",
            "definition": "Числовые характеристики, описывающие рассеяние данных: размах, дисперсия, стандартное отклонение, межквартильный размах.",
            "methods": [
                {"uid": "MET-SPREAD-RANGE", "title": "Вычисление размаха",
                 "description": "Размах R = xmax − xmin. Простейшая мера разброса, чувствительна к выбросам.",
                 "examples": [{"uid": "EX-SPREAD-001", "title": "Размах", "statement": "Данные: 12, 15, 18, 22, 45. Найдите размах.", "solution": "R = 45 − 12 = 33. Большой размах из-за выброса 45."}],
                },
                {"uid": "MET-SPREAD-IQR", "title": "Межквартильный размах (IQR)",
                 "description": "IQR = Q₃ − Q₁. Q₁ — медиана нижней половины, Q₃ — верхней. IQR устойчив к выбросам.",
                 "examples": [{"uid": "EX-SPREAD-002", "title": "IQR", "statement": "Данные: 2, 4, 6, 8, 10, 12, 14. Найдите IQR.", "solution": "Q₁ = 4, Q₃ = 12. IQR = 12 − 4 = 8."}],
                },
                {"uid": "MET-SPREAD-STD", "title": "Стандартное отклонение для оценки разброса",
                 "description": "σ = √D. Правило 68-95-99: ~68% данных в пределах x̄±σ, ~95% в x̄±2σ, ~99% в x̄±3σ.",
                 "examples": [{"uid": "EX-SPREAD-003", "title": "Правило 3 сигм", "statement": "x̄=170 см, σ=10. Какой рост у ~95% людей?", "solution": "170±2·10 = от 150 до 190 см — в этом интервале ~95%."}],
                },
            ],
        }],
    },

    # 25. Меры центральной тенденции
    {
        "topic_uid": "TOP-MERY-CENTRALNOI-TENDENCI-75dcdc",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-CENTRAL-TENDENCY",
            "title": "Меры центральной тенденции",
            "definition": "Числовые характеристики «центра» данных: среднее арифметическое, медиана, мода.",
            "methods": [
                {"uid": "MET-CENT-MEAN", "title": "Среднее арифметическое",
                 "description": "x̄ = Σxᵢ/n. Чувствительно к выбросам. Для взвешенных данных: x̄ = Σwᵢxᵢ/Σwᵢ.",
                 "examples": [{"uid": "EX-CENT-001", "title": "Среднее с выбросом", "statement": "Зарплаты: 30, 32, 35, 33, 200 тыс. руб. Найдите среднее.", "solution": "x̄ = (30+32+35+33+200)/5 = 330/5 = 66 тыс. Среднее завышено выбросом 200."}],
                },
                {"uid": "MET-CENT-MEDIAN", "title": "Медиана",
                 "description": "Упорядочьте данные. Если n нечётное — средний элемент. Если чётное — среднее двух средних. Устойчива к выбросам.",
                 "examples": [{"uid": "EX-CENT-002", "title": "Медиана vs среднее", "statement": "Зарплаты: 30, 32, 33, 35, 200. Найдите медиану.", "solution": "Me = 33 (средний элемент). Медиана 33 лучше отражает «типичную» зарплату, чем среднее 66."}],
                },
                {"uid": "MET-CENT-MODE", "title": "Мода",
                 "description": "Мода — значение с наибольшей частотой. Может быть несколько мод (мультимодальное распределение) или не быть вовсе.",
                 "examples": [{"uid": "EX-CENT-003", "title": "Мода", "statement": "Оценки: 4, 5, 5, 3, 4, 5, 4, 5. Найдите моду.", "solution": "Частоты: 3→1, 4→3, 5→4. Мода = 5 (встречается 4 раза)."}],
                },
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
                            ex_uid = ex["uid"]
                            ex_props = {k: v for k, v in ex.items() if k != "uid"}
                            if not dry_run:
                                _merge_node(session, "Example", ex_uid, ex_props)
                                _merge_rel(session, method_uid, "HAS_EXAMPLE", ex_uid)
                            stats["examples"] += 1; stats["rels"] += 1
    finally:
        repo.close()
    mode = "(DRY RUN)" if dry_run else "(ПРИМЕНЕНО)"
    print(f"\n{'='*60}\nBatch 2 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено связей={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
