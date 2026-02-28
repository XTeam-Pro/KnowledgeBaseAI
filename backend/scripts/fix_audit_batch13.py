#!/usr/bin/env python3
"""Batch 13: Fix last 7 FEW_METHODS topics."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 1. Теория чисел и делимость ЕГЭ (1 → 3)
    {
        "topic_uid": "TOP-EGE-TEORIYA-CHISEL-DELIMOST-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-NUM-THEORY-EGE-B13",
            "title": "Теория чисел и делимость",
            "definition": "Признаки делимости, НОД/НОК, простые числа, сравнения по модулю. Задачи ЕГЭ.",
            "methods": [
                {"uid": "MET-NTE-DIVISIBILITY", "title": "Признаки делимости",
                 "description": "На 2: последняя цифра чётная. На 3: сумма цифр ÷ 3. На 4: последние 2 цифры ÷ 4. На 9: сумма цифр ÷ 9. На 11: разность чередующихся сумм ÷ 11.",
                 "examples": [{"uid": "EX-NTE-001", "title": "Признаки делимости", "statement": "Делится ли 2574 на 6?", "solution": "На 2: 4 — чётная ✓. На 3: 2+5+7+4=18 ÷ 3 ✓. Делится на 6."}]},
                {"uid": "MET-NTE-GCD-LCM", "title": "НОД и НОК в задачах ЕГЭ",
                 "description": "Алгоритм Евклида: НОД(a,b)=НОД(b,a mod b). НОК=ab/НОД(a,b). Применение: дроби, делимость.",
                 "examples": [{"uid": "EX-NTE-002", "title": "НОД в задаче", "statement": "В каком наименьшем числе дней совпадут графики (один каждые 12 дней, другой каждые 18)?", "solution": "НОК(12,18)=36 дней."}]},
                {"uid": "MET-NTE-MODULAR", "title": "Сравнения по модулю в задачах",
                 "description": "a≡b(mod m): a и b дают одинаковый остаток при делении на m. Остатки сохраняются при +,−,·.",
                 "examples": [{"uid": "EX-NTE-003", "title": "Остатки", "statement": "Найдите остаток 7¹⁰⁰ при делении на 5.", "solution": "7≡2(mod 5). 2¹=2, 2²=4, 2³≡3, 2⁴≡1(mod 5). Цикл 4. 100=4·25. 7¹⁰⁰≡1(mod 5). Остаток 1."}]},
            ],
        }],
    },

    # 2. Тригонометрические уравнения: сложные случаи (2 → 3)
    {
        "topic_uid": "TOP-MATH-ADVANCED-TRIG",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ADV-TRIG-B13",
            "title": "Тригонометрические уравнения: сложные случаи",
            "definition": "Уравнения, сводимые к квадратным, однородные, с вспомогательным углом.",
            "methods": [
                {"uid": "MET-ATRIG-QUADRATIC", "title": "Тригонометрические уравнения, сводимые к квадратным",
                 "description": "Замена t=sin x (или cos x, tg x). Решите квадратное t²+bt+c=0. Вернитесь к x: sin x=t₁, sin x=t₂.",
                 "examples": [{"uid": "EX-ATRIG-001", "title": "Замена", "statement": "2cos²x−3cos x+1=0.", "solution": "t=cos x: 2t²−3t+1=0. t=1 или t=1/2. cos x=1: x=2πn. cos x=1/2: x=±π/3+2πn."}]},
                {"uid": "MET-ATRIG-HOMOGENEOUS", "title": "Однородные тригонометрические уравнения",
                 "description": "a·sin²x+b·sin x·cos x+c·cos²x=0. Делите на cos²x → a·tg²x+b·tg x+c=0.",
                 "examples": [{"uid": "EX-ATRIG-002", "title": "Однородное", "statement": "sin²x−3sin x·cos x+2cos²x=0.", "solution": "Делим на cos²x: tg²x−3tg x+2=0. t=tg x: t=1, t=2. x=π/4+πn, x=arctg 2+πn."}]},
                {"uid": "MET-ATRIG-AUX", "title": "Метод вспомогательного угла",
                 "description": "a·sin x+b·cos x = R·sin(x+φ), где R=√(a²+b²), tg φ=b/a. Сводит к простому уравнению.",
                 "examples": [{"uid": "EX-ATRIG-003", "title": "Вспомогательный угол", "statement": "sin x+cos x=1.", "solution": "√2·sin(x+π/4)=1. sin(x+π/4)=1/√2. x+π/4=π/4+2πn → x=2πn. x+π/4=3π/4+2πn → x=π/2+2πn."}]},
            ],
        }],
    },

    # 3. Тригонометрия (2 → 3)
    {
        "topic_uid": "TOP-MATH-TRIGONOMETRY",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-TRIG-B13",
            "title": "Тригонометрия",
            "definition": "Тригонометрические функции, основные тождества, формулы сложения, уравнения.",
            "methods": [
                {"uid": "MET-TRIG-IDENTITIES", "title": "Основные тригонометрические тождества",
                 "description": "sin²α+cos²α=1. tg α=sin α/cos α. 1+tg²α=1/cos²α. Формулы двойного угла: sin 2α=2sin α·cos α.",
                 "examples": [{"uid": "EX-TRIG-001", "title": "Тождество", "statement": "sin α=3/5. Найдите cos α (0<α<π/2).", "solution": "cos²α=1−9/25=16/25. cos α=4/5 (α в I четверти)."}]},
                {"uid": "MET-TRIG-EQUATIONS", "title": "Тригонометрические уравнения",
                 "description": "sin x=a: x=(−1)ⁿarcsin a+πn. cos x=a: x=±arccos a+2πn. tg x=a: x=arctg a+πn.",
                 "examples": [{"uid": "EX-TRIG-002", "title": "Уравнение", "statement": "cos 2x=1/2.", "solution": "2x=±π/3+2πn. x=±π/6+πn."}]},
                {"uid": "MET-TRIG-ADDITION", "title": "Формулы сложения и приведения",
                 "description": "sin(α±β)=sin α cos β±cos α sin β. cos(α±β)=cos α cos β∓sin α sin β. Формулы приведения: sin(π/2−α)=cos α.",
                 "examples": [{"uid": "EX-TRIG-003", "title": "Формула сложения", "statement": "sin 75° = sin(45°+30°).", "solution": "sin 45°cos 30°+cos 45°sin 30°=(√2/2)(√3/2)+(√2/2)(1/2)=(√6+√2)/4."}]},
            ],
        }],
    },

    # 4. Углы (2 → 3)
    {
        "topic_uid": "TOP-UGLY-9cbfc3",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ANGLES-B13",
            "title": "Углы",
            "definition": "Виды углов, измерение, свойства. Смежные, вертикальные, при параллельных прямых.",
            "methods": [
                {"uid": "MET-ANG-TYPES", "title": "Виды углов и их свойства",
                 "description": "Острый: 0°<α<90°. Прямой: 90°. Тупой: 90°<α<180°. Развёрнутый: 180°. Полный: 360°.",
                 "examples": [{"uid": "EX-ANG-001", "title": "Классификация", "statement": "Угол 135°. Какой вид?", "solution": "90°<135°<180° → тупой угол."}]},
                {"uid": "MET-ANG-ADJACENT-VERT", "title": "Смежные и вертикальные углы",
                 "description": "Смежные: сумма 180°. Вертикальные: равны. При пересечении двух прямых — 2 пары вертикальных.",
                 "examples": [{"uid": "EX-ANG-002", "title": "Смежные углы", "statement": "Один из смежных углов = 70°. Другой?", "solution": "180°−70°=110°."}]},
                {"uid": "MET-ANG-PARALLEL", "title": "Углы при параллельных прямых и секущей",
                 "description": "Накрест лежащие: равны. Соответственные: равны. Односторонние: в сумме 180°.",
                 "examples": [{"uid": "EX-ANG-003", "title": "Параллельные прямые", "statement": "a∥b, секущая c. Один из углов 65°. Найдите все остальные.", "solution": "Смежный: 115°. Накрест лежащий: 65°. Соответственный: 65°. Односторонний: 115°."}]},
            ],
        }],
    },

    # 5. Финансовая математика ЕГЭ (1 → 3)
    {
        "topic_uid": "TOP-EGE-FINANSOVAYA-MATEMATIKA-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-FIN-MATH-EGE-B13",
            "title": "Финансовая математика",
            "definition": "Проценты, вклады, кредиты. Задачи ЕГЭ на финансовую грамотность.",
            "methods": [
                {"uid": "MET-FM-SIMPLE-COMPOUND", "title": "Простые и сложные проценты",
                 "description": "Простые: S=P(1+rn). Сложные: S=P(1+r)ⁿ. Сложные выгоднее при n>1.",
                 "examples": [{"uid": "EX-FM-001", "title": "Сложные проценты", "statement": "Вклад 50000 под 8% годовых на 3 года. Итог?", "solution": "S=50000·1.08³=50000·1.2597≈62985 руб."}]},
                {"uid": "MET-FM-CREDIT", "title": "Кредитные расчёты",
                 "description": "Аннуитет: равные платежи. Дифференцированный: убывающие платежи. Формула аннуитета: a=S·r(1+r)ⁿ/((1+r)ⁿ−1).",
                 "examples": [{"uid": "EX-FM-002", "title": "Кредит", "statement": "Кредит 120000 на 2 года, 12% годовых (1% в месяц). Аннуитетный платёж?", "solution": "n=24, r=0.01. a=120000·0.01·1.01²⁴/(1.01²⁴−1)≈5647 руб/мес."}]},
                {"uid": "MET-FM-COMPARE-INVEST", "title": "Сравнение финансовых вариантов",
                 "description": "Сравните полную переплату, итоговую сумму или приведённую стоимость разных предложений.",
                 "examples": [{"uid": "EX-FM-003", "title": "Сравнение", "statement": "Вклад A: 7% на 2 года. Вклад B: 6.5% на 3 года. Какой выгоднее для 100000?", "solution": "A: 100000·1.07²=114490. B: 100000·1.065³=120795. За 3 года B выгоднее (но и срок больше)."}]},
            ],
        }],
    },

    # 6. Числовые последовательности и прогрессии (2 → 3)
    {
        "topic_uid": "TOP-MATH-PROGRESSIONS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PROGRESSIONS-B13",
            "title": "Числовые последовательности и прогрессии",
            "definition": "Арифметическая прогрессия (AP) и геометрическая прогрессия (GP). Формулы n-го члена и суммы.",
            "methods": [
                {"uid": "MET-PROG-AP", "title": "Арифметическая прогрессия",
                 "description": "aₙ=a₁+d(n−1). Sₙ=n(a₁+aₙ)/2=n(2a₁+d(n−1))/2. Свойство: aₙ=(aₙ₋₁+aₙ₊₁)/2.",
                 "examples": [{"uid": "EX-PROG-001", "title": "AP", "statement": "a₁=3, d=5. a₁₀=? S₁₀=?", "solution": "a₁₀=3+5·9=48. S₁₀=10·(3+48)/2=255."}]},
                {"uid": "MET-PROG-GP", "title": "Геометрическая прогрессия",
                 "description": "bₙ=b₁·qⁿ⁻¹. Sₙ=b₁(qⁿ−1)/(q−1) при q≠1. Бесконечная убывающая: S=b₁/(1−q) при |q|<1.",
                 "examples": [{"uid": "EX-PROG-002", "title": "GP", "statement": "b₁=2, q=3. b₅=? S₅=?", "solution": "b₅=2·3⁴=162. S₅=2·(3⁵−1)/(3−1)=2·242/2=242."}]},
                {"uid": "MET-PROG-APPLY", "title": "Применение прогрессий в задачах",
                 "description": "Рост населения — GP. Равномерное накопление — AP. Сложные проценты — GP. Линейный рост — AP.",
                 "examples": [{"uid": "EX-PROG-003", "title": "Задача на GP", "statement": "Бактерии удваиваются каждый час. Начало: 100. Через 8 часов?", "solution": "b₁=100, q=2, n=8. b₈=100·2⁷=12800."}]},
            ],
        }],
    },

    # 7. Экономические задачи ЕГЭ (1 → 3)
    {
        "topic_uid": "TOP-EGE-EKONOMICHESKIE-ZADACHI-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ECON-EGE-B13",
            "title": "Экономические задачи ЕГЭ",
            "definition": "Задачи на оптимизацию прибыли, налоги, кредиты, вклады из ЕГЭ профильного уровня.",
            "methods": [
                {"uid": "MET-ECON-PROFIT", "title": "Оптимизация прибыли",
                 "description": "Прибыль=Доход−Расходы. Доход=Цена·Количество. Составьте функцию прибыли, найдите максимум через производную.",
                 "examples": [{"uid": "EX-ECON-001", "title": "Максимум прибыли", "statement": "Цена p=100−x (x — объём). Себестоимость 20x+500. Максимальная прибыль?", "solution": "Прибыль=(100−x)x−20x−500=−x²+80x−500. П'=−2x+80=0→x=40. П(40)=1100."}]},
                {"uid": "MET-ECON-CREDIT-DETAILED", "title": "Детальный расчёт кредита",
                 "description": "Ежегодно: долг·(1+r)−платёж. Через n лет долг=0. Составьте рекуррентное соотношение и решите.",
                 "examples": [{"uid": "EX-ECON-002", "title": "Расчёт кредита", "statement": "Кредит 1 млн, 20% годовых, равные платежи 2 года. Платёж?", "solution": "Через 1 год: 1000000·1.2−x. Через 2 года: (1200000−x)·1.2−x=0. 1440000−2.2x=0. x≈654545 руб."}]},
                {"uid": "MET-ECON-TAX", "title": "Налоги и социальные выплаты",
                 "description": "НДФЛ=13% (или прогрессивный). Налоговый вычет уменьшает облагаемую базу. Чистый доход=Доход−Налог.",
                 "examples": [{"uid": "EX-ECON-003", "title": "Налоговый вычет", "statement": "Доход 500000. Вычет 200000. НДФЛ 13%. Сумма налога?", "solution": "Облагаемая база: 500000−200000=300000. Налог: 300000·0.13=39000 руб."}]},
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
    print(f"\n{'='*60}\nBatch 13 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
