#!/usr/bin/env python3
"""Batch 5: Определение вероятности, Основные понятия статистики, Отображения, Оценка параметров, Ошибки выборки."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 36. Определение вероятности (7–9 класс)
    {
        "topic_uid": "TOP-OPREDELENIE-VEROYATNOSTI-f1aab2",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PROB-DEF",
            "title": "Определение вероятности события",
            "definition": "Классическое определение: P(A) = m/n, где m — благоприятные исходы, n — все равновозможные исходы.",
            "methods": [
                {"uid": "MET-PROB-CLASSIC", "title": "Классическая формула вероятности",
                 "description": "P(A) = m/n. Шаги: 1) Определите пространство исходов Ω. 2) Подсчитайте n=|Ω|. 3) Подсчитайте m — число исходов, благоприятных A.",
                 "examples": [{"uid": "EX-PROB-DEF-001", "title": "Бросок кубика", "statement": "P(выпадет чётное число)?", "solution": "Ω={1,2,3,4,5,6}, n=6. Чётные: {2,4,6}, m=3. P=3/6=1/2."}]},
                {"uid": "MET-PROB-PROPERTIES", "title": "Свойства вероятности",
                 "description": "0≤P(A)≤1. P(Ω)=1, P(∅)=0. P(Ā)=1−P(A). Для несовместных: P(A∪B)=P(A)+P(B).",
                 "examples": [{"uid": "EX-PROB-DEF-002", "title": "Вероятность противоположного", "statement": "P(дождь)=0.3. P(без дождя)?", "solution": "P(без дождя) = 1 − 0.3 = 0.7."}]},
                {"uid": "MET-PROB-STAT", "title": "Статистическое определение вероятности",
                 "description": "P(A) ≈ частота = (число появлений A) / (число опытов). При большом n частота стремится к вероятности.",
                 "examples": [{"uid": "EX-PROB-DEF-003", "title": "Частота как вероятность", "statement": "Из 200 деталей 8 бракованных. Оцените P(брак).", "solution": "P ≈ 8/200 = 0.04 = 4%."}]},
            ],
        }],
    },

    # 37. Основные понятия статистики
    {
        "topic_uid": "TOP-OSNOVNYE-PONYATIYA-STATI-2d24ef",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-STAT-BASICS",
            "title": "Основные понятия статистики",
            "definition": "Генеральная совокупность, выборка, объём выборки, репрезентативность.",
            "methods": [
                {"uid": "MET-STAT-POPULATION", "title": "Генеральная совокупность и выборка",
                 "description": "Генеральная совокупность — все объекты исследования. Выборка — часть, которую изучают. Выборка должна быть репрезентативной.",
                 "examples": [{"uid": "EX-STAT-BAS-001", "title": "Выборка", "statement": "Изучаем рост учеников школы (800 чел.). Измерили 50. Что есть генеральная совокупность?", "solution": "Генеральная совокупность — все 800 учеников. Выборка — 50 измеренных."}]},
                {"uid": "MET-STAT-TYPES", "title": "Типы данных: количественные и качественные",
                 "description": "Количественные: числовые (рост, оценка). Качественные: категории (цвет, пол). Дискретные vs непрерывные.",
                 "examples": [{"uid": "EX-STAT-BAS-002", "title": "Классификация данных", "statement": "Классифицируйте: рост, цвет глаз, число книг, температура.", "solution": "Рост — количеств., непрерывные. Цвет глаз — качеств. Число книг — количеств., дискретные. Температура — количеств., непрерывные."}]},
                {"uid": "MET-STAT-FREQ", "title": "Частотная таблица и относительные частоты",
                 "description": "Подсчитайте, сколько раз встречается каждое значение. Относительная частота = частота/n.",
                 "examples": [{"uid": "EX-STAT-BAS-003", "title": "Частотная таблица", "statement": "Оценки: 5,4,3,5,4,5,3,4,4,5. Составьте частотную таблицу.", "solution": "3→2 (0.2), 4→4 (0.4), 5→4 (0.4). Σ отн.частот = 1.0. ✓"}]},
            ],
        }],
    },

    # 38. Отображения (9–10 класс, алгебра)
    {
        "topic_uid": "TOP-OTOBRAZHENIYA-eb11ba",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-MAPPINGS",
            "title": "Отображения и функции",
            "definition": "Отображение — правило, сопоставляющее каждому элементу множества A элемент множества B. Инъекция, сюръекция, биекция.",
            "methods": [
                {"uid": "MET-MAP-TYPES", "title": "Типы отображений: инъекция, сюръекция, биекция",
                 "description": "Инъекция (1-в-1): разные элементы → разные образы. Сюръекция (на): каждый элемент B имеет прообраз. Биекция = инъекция + сюръекция.",
                 "examples": [{"uid": "EX-MAP-001", "title": "Определение типа отображения", "statement": "f: ℝ→ℝ, f(x)=x². Инъекция? Сюръекция?", "solution": "Не инъекция: f(2)=f(−2)=4. Не сюръекция: f(x)≥0, нет прообраза для −1. Не биекция."}]},
                {"uid": "MET-MAP-COMPOSE", "title": "Композиция отображений",
                 "description": "(g∘f)(x) = g(f(x)). Сначала применяется f, затем g. Композиция ассоциативна, но не коммутативна.",
                 "examples": [{"uid": "EX-MAP-002", "title": "Композиция", "statement": "f(x)=2x+1, g(x)=x². Найдите (g∘f)(3).", "solution": "f(3)=7, g(7)=49. (g∘f)(3)=49."}]},
                {"uid": "MET-MAP-INVERSE", "title": "Обратное отображение",
                 "description": "Если f — биекция, то существует f⁻¹: f⁻¹(f(x))=x. Для нахождения: запишите y=f(x), выразите x через y.",
                 "examples": [{"uid": "EX-MAP-003", "title": "Обратная функция", "statement": "f(x)=3x−5. Найдите f⁻¹(x).", "solution": "y=3x−5 → x=(y+5)/3. f⁻¹(x)=(x+5)/3."}]},
            ],
        }],
    },

    # 39. Оценка параметров распределений
    {
        "topic_uid": "TOP-OCENKA-PARAMETROV-RASPRE-f0b295",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PARAM-ESTIMATION",
            "title": "Оценка параметров распределений",
            "definition": "Точечные и интервальные оценки параметров: выборочное среднее, дисперсия, доверительный интервал.",
            "methods": [
                {"uid": "MET-PARAM-POINT", "title": "Точечные оценки параметров",
                 "description": "Выборочное среднее x̄ → оценка μ. Выборочная дисперсия s² → оценка σ². Несмещённая дисперсия: s²=Σ(xᵢ−x̄)²/(n−1).",
                 "examples": [{"uid": "EX-PARAM-001", "title": "Точечная оценка", "statement": "Выборка: 12, 15, 14, 13, 16. Оцените μ и σ².", "solution": "x̄=14 → μ̂=14. s²=[(−2)²+1²+0²+(−1)²+2²]/(5−1)=10/4=2.5."}]},
                {"uid": "MET-PARAM-CONFINT", "title": "Доверительный интервал для среднего",
                 "description": "x̄ ± z·(σ/√n). Для 95% доверия z≈1.96. Чем больше n, тем у́же интервал.",
                 "examples": [{"uid": "EX-PARAM-002", "title": "Доверительный интервал", "statement": "x̄=50, σ=10, n=100. 95%-й доверительный интервал?", "solution": "50 ± 1.96·(10/√100) = 50 ± 1.96 = (48.04; 51.96)."}]},
                {"uid": "MET-PARAM-SAMPLE-SIZE", "title": "Определение необходимого объёма выборки",
                 "description": "n = (z·σ/E)², где E — желаемая точность. Для 95%: n = (1.96·σ/E)².",
                 "examples": [{"uid": "EX-PARAM-003", "title": "Объём выборки", "statement": "σ≈5, точность E=1, доверие 95%. Какой n нужен?", "solution": "n = (1.96·5/1)² = 9.8² ≈ 96.04 → n=97."}]},
            ],
        }],
    },

    # 40. Ошибки выборки
    {
        "topic_uid": "TOP-OSHIBKI-VYBORKI-024504",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-SAMPLING-ERRORS",
            "title": "Ошибки выборки и репрезентативность",
            "definition": "Выборочная ошибка: отклонение выборочной характеристики от генеральной. Систематические и случайные ошибки.",
            "methods": [
                {"uid": "MET-SERR-TYPES", "title": "Типы ошибок выборки",
                 "description": "Случайная ошибка — из-за конечного объёма выборки (уменьшается при ↑n). Систематическая — из-за нерепрезентативности (не зависит от n).",
                 "examples": [{"uid": "EX-SERR-001", "title": "Систематическая ошибка", "statement": "Опрос в интернете о доходах. Почему результат может быть смещён?", "solution": "Систематическая ошибка: не все имеют интернет-доступ, выборка не репрезентативна."}]},
                {"uid": "MET-SERR-MARGIN", "title": "Предельная ошибка выборки",
                 "description": "Δ = z·(σ/√n). Для 95%: Δ = 1.96·σ/√n. Показывает максимальное отклонение x̄ от μ с заданной вероятностью.",
                 "examples": [{"uid": "EX-SERR-002", "title": "Предельная ошибка", "statement": "σ=8, n=64. Найдите предельную ошибку (95%).", "solution": "Δ = 1.96·8/√64 = 1.96·8/8 = 1.96."}]},
                {"uid": "MET-SERR-REDUCE", "title": "Способы уменьшения ошибки выборки",
                 "description": "1) Увеличить n (ошибка ∝ 1/√n). 2) Использовать случайный отбор. 3) Стратифицировать выборку по группам.",
                 "examples": [{"uid": "EX-SERR-003", "title": "Уменьшение ошибки", "statement": "Ошибка = 4 при n=25. Какой n нужен для ошибки = 2?", "solution": "Ошибка ∝ 1/√n. 4/2 = √(n_new/25) → 2 = √(n_new/25) → n_new = 100."}]},
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
    print(f"\n{'='*60}\nBatch 5 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
