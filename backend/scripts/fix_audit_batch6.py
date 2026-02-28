#!/usr/bin/env python3
"""Batch 6: Первообразная, Периметр и площадь, Планиметрия ЕГЭ, Порядок действий, Применение распределений."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 41. Первообразная (10–11 класс)
    {
        "topic_uid": "TOP-PERVOOBRAZNAYA-e23096",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ANTIDERIV",
            "title": "Первообразная и неопределённый интеграл",
            "definition": "F(x) — первообразная f(x), если F'(x)=f(x). Неопределённый интеграл: ∫f(x)dx = F(x)+C.",
            "methods": [
                {"uid": "MET-ANTI-TABLE", "title": "Таблица первообразных",
                 "description": "∫xⁿdx = xⁿ⁺¹/(n+1)+C. ∫sin x dx = −cos x+C. ∫cos x dx = sin x+C. ∫eˣdx = eˣ+C. ∫(1/x)dx = ln|x|+C.",
                 "examples": [{"uid": "EX-ANTI-001", "title": "Табличный интеграл", "statement": "Найдите ∫(3x²+2x)dx.", "solution": "∫3x²dx + ∫2xdx = x³ + x² + C."}]},
                {"uid": "MET-ANTI-RULES", "title": "Правила нахождения первообразных",
                 "description": "∫(af+bg)dx = a∫fdx + b∫gdx (линейность). ∫f(ax+b)dx = F(ax+b)/a + C.",
                 "examples": [{"uid": "EX-ANTI-002", "title": "Линейная замена", "statement": "Найдите ∫cos(2x+3)dx.", "solution": "∫cos(2x+3)dx = sin(2x+3)/2 + C."}]},
                {"uid": "MET-ANTI-VERIFY", "title": "Проверка первообразной дифференцированием",
                 "description": "Чтобы проверить: продифференцируйте результат. Если получится подынтегральная функция — ответ верен.",
                 "examples": [{"uid": "EX-ANTI-003", "title": "Проверка", "statement": "F(x)=x³+x²+C — первообразная для 3x²+2x?", "solution": "F'(x) = 3x²+2x ✓ — совпадает с подынтегральной функцией."}]},
            ],
        }],
    },

    # 42. Периметр и площадь (3–5 класс, Виленкин)
    {
        "topic_uid": "TOP-PERIMETR-I-PLOSHCHAD-003",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PERIM-AREA",
            "title": "Вычисление периметра и площади фигур",
            "definition": "Периметр — сумма длин сторон. Площадь — мера поверхности фигуры.",
            "methods": [
                {"uid": "MET-PA-RECT", "title": "Периметр и площадь прямоугольника",
                 "description": "P = 2(a+b). S = a·b. Для квадрата: P = 4a, S = a².",
                 "examples": [{"uid": "EX-PA-001", "title": "Прямоугольник", "statement": "a=5 см, b=3 см. P=? S=?", "solution": "P = 2(5+3) = 16 см. S = 5·3 = 15 см²."}]},
                {"uid": "MET-PA-TRIANGLE", "title": "Периметр и площадь треугольника",
                 "description": "P = a+b+c. S = (1/2)·a·h, где h — высота к стороне a. Формула Герона: S = √[p(p−a)(p−b)(p−c)], p=(a+b+c)/2.",
                 "examples": [{"uid": "EX-PA-002", "title": "Площадь треугольника", "statement": "Основание 8 см, высота 5 см. S=?", "solution": "S = (1/2)·8·5 = 20 см²."}]},
                {"uid": "MET-PA-COMPLEX", "title": "Площадь составных фигур",
                 "description": "Разбейте сложную фигуру на простые (прямоугольники, треугольники). Найдите площадь каждой и сложите.",
                 "examples": [{"uid": "EX-PA-003", "title": "Г-образная фигура", "statement": "Г-образная комната: 5×3 и 2×4. S=?", "solution": "S = 5·3 + 2·4 = 15 + 8 = 23 м²."}]},
            ],
        }],
    },

    # 43. Планиметрические задачи ЕГЭ
    {
        "topic_uid": "TOP-EGE-PLANIMETRIYA-ZADACHI-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EGE-PLANIM",
            "title": "Решение планиметрических задач ЕГЭ",
            "definition": "Комплексные задачи на свойства треугольников, четырёхугольников, окружностей.",
            "methods": [
                {"uid": "MET-PLANIM-SIMILAR", "title": "Метод подобия треугольников",
                 "description": "Найдите пару подобных треугольников (по двум углам, или стороны пропорциональны). Составьте пропорцию сторон.",
                 "examples": [{"uid": "EX-PLANIM-001", "title": "Подобие", "statement": "В △ABC: DE∥BC, AD=3, DB=6, DE=4. Найдите BC.", "solution": "△ADE∼△ABC, k=AD/AB=3/9=1/3. BC=DE/k=4·3=12."}]},
                {"uid": "MET-PLANIM-AREA", "title": "Метод площадей",
                 "description": "Выразите площадь фигуры двумя способами и приравняйте. Используйте S=½ab·sin C, формулу Герона.",
                 "examples": [{"uid": "EX-PLANIM-002", "title": "Метод площадей", "statement": "В △ABC: AB=13, BC=14, AC=15. Найдите высоту BH.", "solution": "p=(13+14+15)/2=21. S=√(21·8·7·6)=84. S=½·AC·BH → 84=½·15·BH → BH=11.2."}]},
                {"uid": "MET-PLANIM-CIRCLE", "title": "Свойства вписанной и описанной окружностей",
                 "description": "r=S/p (вписанная). R=abc/(4S) (описанная). Угол между касательной и хордой = ½ дуги.",
                 "examples": [{"uid": "EX-PLANIM-003", "title": "Радиус вписанной", "statement": "△ABC: a=13, b=14, c=15, S=84. Найдите r.", "solution": "p=21. r=S/p=84/21=4."}]},
            ],
        }],
    },

    # 44. Порядок действий (2–3 класс, Виленкин/Моро)
    {
        "topic_uid": "TOP-PORYADOK-DEJSTVIJ-006",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ORDER-OPS",
            "title": "Порядок выполнения арифметических действий",
            "definition": "Правила приоритета: скобки → степени → умножение/деление → сложение/вычитание.",
            "methods": [
                {"uid": "MET-ORD-PRIORITY", "title": "Правило приоритета операций",
                 "description": "1) Выполните действия в скобках. 2) Степени и корни. 3) Умножение и деление (слева направо). 4) Сложение и вычитание (слева направо).",
                 "examples": [{"uid": "EX-ORD-001", "title": "Приоритет", "statement": "Вычислите: 2 + 3 × 4.", "solution": "Сначала умножение: 3×4=12. Потом сложение: 2+12=14."}]},
                {"uid": "MET-ORD-BRACKETS", "title": "Использование скобок для изменения порядка",
                 "description": "Скобки имеют наивысший приоритет. (2+3)×4 ≠ 2+3×4. Вложенные скобки — изнутри наружу.",
                 "examples": [{"uid": "EX-ORD-002", "title": "Скобки", "statement": "Вычислите: (2 + 3) × 4.", "solution": "Сначала скобки: 2+3=5. Потом: 5×4=20."}]},
                {"uid": "MET-ORD-MULTI-STEP", "title": "Многошаговые вычисления",
                 "description": "Разбейте выражение на шаги по приоритету. Записывайте промежуточные результаты.",
                 "examples": [{"uid": "EX-ORD-003", "title": "Многошаговое", "statement": "48 ÷ (2 × (3 + 1)) − 2.", "solution": "1) 3+1=4. 2) 2×4=8. 3) 48÷8=6. 4) 6−2=4. Ответ: 4."}]},
            ],
        }],
    },

    # 45. Применение вероятностных распределений
    {
        "topic_uid": "TOP-PRIMENENIE-VEROYATNOSTNY-3216ba",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-DISTR-APPLY",
            "title": "Применение вероятностных распределений",
            "definition": "Использование распределений для решения практических задач: контроль качества, прогнозирование, оценка рисков.",
            "methods": [
                {"uid": "MET-DAPPLY-BINOM", "title": "Применение биномиального распределения",
                 "description": "P(X=k) = C(n,k)·pᵏ·qⁿ⁻ᵏ. Используется для подсчёта числа успехов в n независимых испытаниях.",
                 "examples": [{"uid": "EX-DAPPLY-001", "title": "Контроль качества", "statement": "P(брак)=0.05. Из 10 деталей. P(ровно 1 бракованная)?", "solution": "P(X=1) = C(10,1)·0.05¹·0.95⁹ = 10·0.05·0.630 = 0.315."}]},
                {"uid": "MET-DAPPLY-NORMAL", "title": "Применение нормального распределения",
                 "description": "Стандартизация Z=(X−μ)/σ, затем по таблице Φ(z). Используется для непрерывных величин.",
                 "examples": [{"uid": "EX-DAPPLY-002", "title": "Производственный допуск", "statement": "Диаметр детали: μ=50мм, σ=0.2мм. P(49.6<X<50.4)?", "solution": "Z₁=(49.6−50)/0.2=−2, Z₂=(50.4−50)/0.2=2. P(−2<Z<2)≈0.954=95.4%."}]},
                {"uid": "MET-DAPPLY-EXPECT", "title": "Использование E(X) для принятия решений",
                 "description": "Сравните E(X) для разных стратегий. Выбирайте стратегию с наибольшим E (или наименьшим E потерь).",
                 "examples": [{"uid": "EX-DAPPLY-003", "title": "Выбор стратегии", "statement": "Страховка: 1000 руб/год. P(ущерб 50000)=0.03. Стоит ли страховаться?", "solution": "E(ущерба без страховки)=50000·0.03=1500 руб. Страховка 1000 < 1500 → выгодно."}]},
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
    print(f"\n{'='*60}\nBatch 6 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
