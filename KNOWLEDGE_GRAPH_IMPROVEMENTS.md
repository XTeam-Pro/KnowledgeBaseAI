# Knowledge Graph Improvements — Стратегический план развития

> **Версия**: 1.1
> **Дата**: 2026-04-03
> **Статус**: RFC (Revised, phased MVP)
> **Область**: KnowledgeBaseAI — Neo4j graph topology, architecture, scalability

---

## Содержание

1. [Текущее состояние](#1-текущее-состояние)
2. [P0 — Orphan-сущности и валидация целостности](#2-p0--orphan-сущности-и-валидация-целостности)
3. [P1 — Weighted PREREQ](#3-p1--weighted-prereq)
4. [P2 — Misconception Nodes](#4-p2--misconception-nodes)
5. [P3 — Skill Composition Graph](#5-p3--skill-composition-graph)
6. [P4 — Neo4j Vector Index (замена Qdrant)](#6-p4--neo4j-vector-index-замена-qdrant)
7. [P5 — Learner State Layer (PostgreSQL-first)](#7-p5--learner-state-layer-postgresql-first)
8. [P6 — Bloom Taxonomy Levels](#8-p6--blooms-taxonomy-levels)
9. [P7 — Multi-Subject Cross-Links](#9-p7--multi-subject-cross-links)
10. [P8 — Adaptive Difficulty Micro-Graph](#10-p8--adaptive-difficulty-micro-graph)
11. [P9 — Knowledge Graph Versioning и A/B-тестирование топологий](#11-p9--knowledge-graph-versioning-и-ab-тестирование-топологий)
12. [Сводная матрица изменений](#12-сводная-матрица-изменений)
13. [Порядок миграции](#13-порядок-миграции)

---

## 1. Текущее состояние

### 1.1 Топология

```
Subject (1: Mathematics)
  └── Section (13)
       └── Subsection (38)
            └── Topic (224)
                 ├── REQUIRES_SKILL → Skill (1,026)
                 │    └── HAS_METHOD → Method (1,985)
                 │         └── HAS_EXAMPLE → Example (2,654)
                 └── PREREQ → Topic
```

| Метрика | Значение |
|---------|----------|
| Всего сущностей | 6,054 |
| Всего связей | 6,317 |
| Типы связей | CONTAINS, PREREQ, REQUIRES_SKILL, HAS_METHOD, HAS_EXAMPLE |
| PREREQ-рёбер | 221 (Topic→Topic) |
| Кросс-секционных PREREQ | 89 (40% от всех) |
| Корневых тем (in-degree=0) | 80 |
| Листовых тем (out-degree=0) | 124 |
| Макс. PREREQ in-degree | 16 |
| Макс. PREREQ out-degree | 6 |
| Классы | 2–11 (99–141 тем на класс) |
| Orphan-сущностей (нет `_label`) | 113 |

### 1.2 Текущий стек

- **Neo4j 5.26** — граф знаний (Topic, Skill, Method, Example, PREREQ)
- **PostgreSQL 15** — proposals, audit, curricula, learner mastery
- **Qdrant** — vector embeddings для semantic search (collection `concepts`, 1536-dim)
- **Redis** — кэш roadmap, question cache, events

### 1.3 Ключевые паттерны

- Все мутации графа проходят через **Proposal → Review → Commit** pipeline
- Integrity checks: циклы PREREQ (NetworkX), orphan skills, hierarchy compliance
- Canonical spec: `ALLOWED_NODE_LABELS` (14 типов), `ALLOWED_EDGE_TYPES` (11 типов)
- Roadmap planner: топологическая сортировка PREREQ + mastery scoring
- Mastery update: Bayesian `new = prior + 0.4 * confidence * (score - prior)`

---

## 2. P0 — Orphan-сущности и валидация целостности

### 2.1 Проблема

В дампе `graph_entities.jsonl` обнаружено **113 сущностей без `_label`**. Все они имеют поле `type` (Method/Example), но не были корректно маркированы при создании. Примеры:

```
MET-INTRO-NERAVENSTVA-S-DVUMYA-PEREMENNYMI  type=Method
EX-INTRO-NERAVENSTVA-S-DVUMYA-PEREMENNYMI-01  type=Example
EX-LI-GRAPHIC-01  type=Example
MET-NERAV-DVE-PEREM-SISTEMA  type=Method
```

Эти сущности:
- Не индексируются в Qdrant (indexer проверяет тип по Neo4j-label)
- Не возвращаются в viewport-запросах (фильтрация по label)
- Не участвуют в integrity checks
- Не попадают в roadmap

### 2.2 Корневая причина

При batch-импорте через `load_data.py` / `push_to_neo4j.py` поле `_label` не было установлено для записей, добавленных отдельным proposal-ом (тема «Неравенства с двумя переменными»). Система proposal при `CREATE_NODE` устанавливает Neo4j label из поля `_label` JSONL, но если оно отсутствует — узел создаётся без label.

### 2.3 Решение

#### 2.3.1 Одноразовая миграция — исправление существующих orphan-узлов

```cypher
// Шаг 1: Найти все узлы без стандартного label
MATCH (n)
WHERE n.tenant_id = 'default'
  AND n.type IS NOT NULL
  AND NOT n:Subject AND NOT n:Section AND NOT n:Subsection
  AND NOT n:Topic AND NOT n:Skill AND NOT n:Method
  AND NOT n:Example AND NOT n:Concept AND NOT n:Formula
  AND NOT n:TaskType AND NOT n:Goal AND NOT n:Objective
  AND NOT n:Error AND NOT n:ContentUnit
RETURN n.uid AS uid, n.type AS type, n.title AS title
ORDER BY n.type, n.uid
```

```cypher
// Шаг 2: Назначить label на основе поля type
// Для Method-узлов:
MATCH (n)
WHERE n.tenant_id = 'default'
  AND n.type = 'Method'
  AND NOT n:Method
SET n:Method
RETURN count(n) AS fixed_methods

// Для Example-узлов:
MATCH (n)
WHERE n.tenant_id = 'default'
  AND n.type = 'Example'
  AND NOT n:Example
SET n:Example
RETURN count(n) AS fixed_examples
```

#### 2.3.2 Защита в коде — валидация при commit

Файл: `backend/app/workers/commit.py`

В функции `_apply_ops_tx` добавить проверку перед `CREATE_NODE`:

```python
def _validate_node_label(op: dict) -> None:
    """Убедиться, что у операции CREATE_NODE есть валидный _label."""
    label = op.get("data", {}).get("_label")
    if not label:
        raise IntegrityError(
            f"CREATE_NODE operation for uid={op.get('uid')} "
            f"is missing required '_label' field"
        )
    if label not in ALLOWED_NODE_LABELS:
        raise IntegrityError(
            f"Label '{label}' not in ALLOWED_NODE_LABELS for uid={op.get('uid')}"
        )
```

#### 2.3.3 CI-валидатор JSONL-дампов

Скрипт `backend/scripts/validate_graph_dump.py`:

```python
"""
Валидация graph_entities.jsonl и graph_relationships.jsonl.
Проверяет:
  1. Все сущности имеют _label из ALLOWED_NODE_LABELS
  2. Все связи имеют _type из ALLOWED_EDGE_TYPES
  3. Все _from_uid и _to_uid ссылаются на существующие сущности
  4. Нет дубликатов uid
  5. Нет циклов в PREREQ
  6. Иерархия CONTAINS корректна (Subject→Section→Subsection→Topic)
"""
import json
import sys
from pathlib import Path

ALLOWED_NODE_LABELS = {
    "Subject", "Section", "Subsection", "Topic", "Skill", "Method",
    "Goal", "Objective", "Example", "Error", "ContentUnit",
    "Concept", "Formula", "TaskType"
}

ALLOWED_EDGE_TYPES = {
    "CONTAINS", "PREREQ", "USES_SKILL", "LINKED", "TARGETS",
    "HAS_EXAMPLE", "HAS_UNIT", "MEASURES", "BASED_ON",
    "REQUIRES_SKILL", "HAS_METHOD"
}

def validate(entities_path: Path, rels_path: Path) -> list[str]:
    errors = []
    uids = set()
    uid_to_label = {}

    # Validate entities
    with open(entities_path) as f:
        for i, line in enumerate(f, 1):
            obj = json.loads(line)
            uid = obj.get("uid")

            if not uid:
                errors.append(f"entities:{i}: missing uid")
                continue

            if uid in uids:
                errors.append(f"entities:{i}: duplicate uid={uid}")
            uids.add(uid)

            label = obj.get("_label")
            if not label:
                errors.append(f"entities:{i}: uid={uid} missing _label (type={obj.get('type')})")
            elif label not in ALLOWED_NODE_LABELS:
                errors.append(f"entities:{i}: uid={uid} invalid _label={label}")

            uid_to_label[uid] = label

    # Validate relationships
    with open(rels_path) as f:
        for i, line in enumerate(f, 1):
            obj = json.loads(line)
            rtype = obj.get("_type", obj.get("type"))
            from_uid = obj.get("_from_uid", obj.get("from_uid"))
            to_uid = obj.get("_to_uid", obj.get("to_uid"))

            if rtype not in ALLOWED_EDGE_TYPES:
                errors.append(f"rels:{i}: invalid type={rtype}")
            if from_uid not in uids:
                errors.append(f"rels:{i}: dangling _from_uid={from_uid}")
            if to_uid not in uids:
                errors.append(f"rels:{i}: dangling _to_uid={to_uid}")

    return errors


if __name__ == "__main__":
    base = Path(__file__).parent.parent / "app" / "services" / "kb"
    errors = validate(base / "graph_entities.jsonl", base / "graph_relationships.jsonl")
    if errors:
        print(f"FAILED: {len(errors)} errors")
        for e in errors[:50]:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("OK: all validations passed")
```

### 2.4 Критерии завершения

- [ ] Все 113 orphan-узлов получили корректный Neo4j label
- [ ] `commit.py` отклоняет CREATE_NODE без `_label`
- [ ] CI запускает `validate_graph_dump.py` при изменениях в `services/kb/`
- [ ] Orphan-узлы появляются в viewport и индексируются в Qdrant

---

## 3. P1 — Weighted PREREQ

### 3.1 Проблема

Текущие PREREQ-связи бинарны: тема A либо зависит от темы B, либо нет. В реальности зависимости имеют разную силу:

- «Квадратные уравнения» **необходимы** для «Тригонометрических уравнений» (weight ~0.95)
- «Графики функций» **полезны** для «Тригонометрических уравнений» (weight ~0.30)
- «Комбинаторика» **слабо связана** с «Тригонометрическими уравнениями» (weight ~0.05)

Без весов roadmap planner вынужден требовать прохождения ВСЕХ пререквизитов перед разблокировкой темы. Это:
- Замедляет прогресс сильных учеников
- Создаёт искусственные bottleneck-и (тема с in-degree=16 блокирована пока не пройдены все 16)
- Не позволяет строить «быстрые пути» для подготовки к конкретному экзаменационному заданию

### 3.2 Модель данных

#### 3.2.1 Новые свойства ребра PREREQ

```
(:Topic)-[:PREREQ {
    weight: Float,          // 0.0–1.0, сила зависимости
    aspect: String,         // категория: "algebraic", "geometric", "notational", "conceptual"
    is_hard: Boolean,       // true = блокирующий (без него невозможно), false = мягкий
    description: String     // почему эта зависимость существует
}]->(:Topic)
```

| Свойство | Тип | Обязательное | По умолчанию | Описание |
|----------|-----|-------------|-------------|----------|
| `weight` | Float | Да | 0.5 | Сила зависимости: 0.0 (декоративная) — 1.0 (блокирующая) |
| `aspect` | String | Нет | `null` | Семантическая категория: `"algebraic"`, `"geometric"`, `"notational"`, `"conceptual"`, `"computational"` |
| `is_hard` | Boolean | Нет | `false` | Жёсткая зависимость: без неё тема НЕ может быть начата |
| `description` | String | Нет | `null` | Человеко-читаемое объяснение связи |

#### 3.2.2 Пороговая модель

Для разблокировки темы T, у которой есть N пререквизитов с весами w_i и mastery-значениями m_i:

```
readiness(T) = Σ(w_i * m_i) / Σ(w_i)

Тема разблокирована, если:
  1. Все hard-prereq имеют mastery ≥ 0.5
  2. readiness(T) ≥ threshold (настраиваемый, по умолчанию 0.6)
```

Это заменяет текущую бинарную логику «все prereq пройдены» на градиентную шкалу.

#### 3.2.3 Пример

```
Topic "Тригонометрические уравнения":
  PREREQ → "Квадратные уравнения"    weight=0.9  is_hard=true   aspect="algebraic"
  PREREQ → "Графики функций"          weight=0.3  is_hard=false  aspect="conceptual"
  PREREQ → "Тригонометрические функции" weight=0.95 is_hard=true  aspect="conceptual"
  PREREQ → "Радианная мера"            weight=0.4  is_hard=false  aspect="notational"

Ученик с mastery:
  "Квадратные уравнения" = 0.7
  "Графики функций"      = 0.2
  "Триг. функции"        = 0.8
  "Радианная мера"        = 0.0

readiness = (0.9*0.7 + 0.3*0.2 + 0.95*0.8 + 0.4*0.0) / (0.9+0.3+0.95+0.4)
         = (0.63 + 0.06 + 0.76 + 0.0) / 2.55
         = 1.45 / 2.55 = 0.569

Hard-prereq check: "Квадратные" mastery=0.7 ≥ 0.5 ✓, "Триг. функции" mastery=0.8 ≥ 0.5 ✓
readiness=0.569 < 0.6 → тема ещё не разблокирована (нужно немного подтянуть «Радианную меру»)
```

### 3.3 Миграция Neo4j

```cypher
// Шаг 1: Установить weight=0.5 на все существующие PREREQ (нейтральное значение)
MATCH ()-[r:PREREQ]->()
WHERE r.weight IS NULL
SET r.weight = 0.5, r.is_hard = false
RETURN count(r) AS updated

// Шаг 2: Пометить очевидно жёсткие зависимости
// (same subsection, high structural coupling)
MATCH (parent:Subsection)-[:CONTAINS]->(t1:Topic),
      (parent)-[:CONTAINS]->(t2:Topic),
      (t1)-[r:PREREQ]->(t2)
SET r.weight = 0.8, r.is_hard = true
RETURN count(r) AS hard_set

// Шаг 3: Кросс-секционные зависимости — умеренный вес
MATCH (s1:Section)-[:CONTAINS]->(:Subsection)-[:CONTAINS]->(t1:Topic),
      (s2:Section)-[:CONTAINS]->(:Subsection)-[:CONTAINS]->(t2:Topic),
      (t1)-[r:PREREQ]->(t2)
WHERE s1 <> s2
SET r.weight = 0.4
RETURN count(r) AS cross_section_set
```

### 3.4 Изменения в коде

#### 3.4.1 Canonical spec

Файл: `backend/app/core/canonical.py`

Добавить в правила для PREREQ:

```python
PREREQ_SCHEMA = {
    "weight": {"type": "float", "min": 0.0, "max": 1.0, "required": True},
    "aspect": {
        "type": "string",
        "enum": ["algebraic", "geometric", "notational", "conceptual", "computational"],
        "required": False
    },
    "is_hard": {"type": "bool", "required": False, "default": False},
    "description": {"type": "string", "required": False},
}
```

#### 3.4.2 Roadmap planner

Файл: `backend/app/services/roadmap_planner.py`

Текущая логика `plan_route`:

```python
# Текущее: бинарная проверка
unmet = [p for p in prereqs if progress.get(p, 0.0) < 0.5]
if unmet:
    readiness = 0.0
```

Новая логика:

```python
def _compute_readiness(
    prereq_edges: list[dict],
    progress: dict[str, float],
    threshold: float = 0.6,
) -> tuple[float, bool]:
    """
    Возвращает (readiness_score, is_unlocked).

    prereq_edges: [{"to_uid": "...", "weight": 0.9, "is_hard": True}, ...]
    progress: {"topic_uid": mastery_float, ...}
    """
    if not prereq_edges:
        return 1.0, True

    total_weight = 0.0
    weighted_mastery = 0.0
    hard_blocked = False

    for edge in prereq_edges:
        w = edge.get("weight", 0.5)
        mastery = progress.get(edge["to_uid"], 0.0)
        total_weight += w
        weighted_mastery += w * mastery

        if edge.get("is_hard") and mastery < 0.5:
            hard_blocked = True

    readiness = weighted_mastery / total_weight if total_weight > 0 else 1.0
    is_unlocked = not hard_blocked and readiness >= threshold

    return readiness, is_unlocked
```

#### 3.4.3 Cypher-запрос для roadmap с весами

```cypher
MATCH (t:Topic)
WHERE t.tenant_id = $tenant_id
OPTIONAL MATCH (t)-[pr:PREREQ]->(dep:Topic)
RETURN t.uid AS uid,
       t.title AS title,
       t.difficulty_level AS difficulty,
       t.user_class_min AS class_min,
       t.user_class_max AS class_max,
       collect({
           to_uid: dep.uid,
           weight: coalesce(pr.weight, 0.5),
           is_hard: coalesce(pr.is_hard, false),
           aspect: pr.aspect
       }) AS prereqs
ORDER BY t.uid
```

### 3.5 Integrity check

Файл: `backend/app/services/integrity.py`

Добавить:

```python
def check_prereq_weights(rels: list[dict]) -> list[str]:
    """Проверяет, что все PREREQ имеют валидный weight."""
    violations = []
    for rel in rels:
        if rel.get("type") == "PREREQ":
            w = rel.get("properties", {}).get("weight")
            if w is None:
                violations.append(f"PREREQ {rel['from_uid']}→{rel['to_uid']}: missing weight")
            elif not (0.0 <= w <= 1.0):
                violations.append(f"PREREQ {rel['from_uid']}→{rel['to_uid']}: weight={w} out of [0,1]")
    return violations
```

### 3.6 API-контракт

Endpoint `GET /v1/engine/roadmap` — response дополняется:

```json
{
  "items": [
    {
      "uid": "TOP-TRIGONOMETRICHESKIE-URAVNENIYA",
      "title": "Тригонометрические уравнения",
      "mastery": 0.0,
      "readiness": 0.569,
      "is_unlocked": false,
      "prereqs": [
        {"uid": "TOP-KVADRATNYE-URAVNENIYA", "weight": 0.9, "is_hard": true, "mastery": 0.7},
        {"uid": "TOP-GRAFIKI-FUNKCIJ", "weight": 0.3, "is_hard": false, "mastery": 0.2}
      ],
      "blocking_prereqs": ["TOP-RADIANNAYA-MERA"]
    }
  ]
}
```

### 3.7 Стратегия наполнения весами

1. **Фаза 1 (автоматическая)**: Все PREREQ получают `weight=0.5`. Intra-subsection PREREQ → `weight=0.8, is_hard=true`. Cross-section → `weight=0.4`.
2. **Фаза 2 (data-driven)**: По мере накопления данных о поведении учеников — корректировать веса на основе корреляции: если ученики с низким mastery по prereq B всё равно успешно проходят тему A → уменьшить weight.
3. **Фаза 3 (expert review)**: Дать преподавателям UI для ручной калибровки весов.

### 3.8 План реализации «реальных базовых весов PREREQ» (graph-invariant)

Цель: уйти от массового `0.5` и заполнить граф **контентными базовыми весами**, не смешивая их с персонализацией.

#### 3.8.1 Принцип разделения ответственности

- Neo4j (граф): `PREREQ.weight`, `PREREQ.is_hard` — только **базовая предметная истина**.
- PostgreSQL (StudyNinja): персональные коэффициенты влияния пререквизитов для конкретного пользователя.
- Runtime: `effective_weight = graph_weight * user_factor`, при этом `graph_weight` в Neo4j не мутирует от поведения отдельных учеников.

#### 3.8.2 Этапы внедрения

1. **Этап A (неделя 1): подготовка датасета рёбер**
   - Экспорт всех `PREREQ` в рабочий файл `prereq_weight_baseline.csv`.
   - Поля: `from_topic_uid`, `to_prereq_uid`, `from_title`, `to_title`, `same_subsection`, `same_section`, `current_weight`, `is_hard`.
   - Отдельно пометить рёбра с `current_weight=0.5` как кандидаты на калибровку.

2. **Этап B (недели 1–2): экспертная разметка top-priority**
   - Приоритет 1: топ-100 тем по трафику/экзаменационной значимости.
   - Шкала весов: `0.2, 0.4, 0.6, 0.8, 1.0`.
   - Правило `is_hard=true` только если без prereq запуск темы педагогически некорректен.
   - Артефакт: `prereq_weights_v1.csv` (версионируется в репозитории).

3. **Этап C (неделя 2): массовое применение в граф**
   - Batch-upsert из `prereq_weights_v1.csv` в Neo4j.
   - Изменяются только `weight`/`is_hard` для существующих `PREREQ`.
   - Все изменения проходят через Proposal → Review → Commit pipeline.

4. **Этап D (неделя 3): QA и стабилизация**
   - Проверка инвариантов: циклы, out-of-range weight, чрезмерные hard-block chains.
   - Проверка продукта: unlocked-rate/false-blocked-rate на контрольной выборке.
   - После QA — расширение покрытия со 100 тем на весь предмет.

#### 3.8.3 Технические артефакты

- Файл источника правды: `backend/app/services/kb/prereq_weights_v1.csv`.
- Скрипт применения: `backend/scripts/apply_prereq_weights.py`.
- Отчёт покрытия: `backend/scripts/report_prereq_weight_coverage.py`.

Пример метрики покрытия:

```cypher
MATCH ()-[r:PREREQ]->()
RETURN count(r) AS total,
       count(CASE WHEN r.weight IS NOT NULL THEN 1 END) AS with_weight,
       count(CASE WHEN coalesce(r.weight, 0.5) = 0.5 THEN 1 END) AS still_default
```

#### 3.8.4 Гейты качества для релиза

- `still_default / total <= 20%` на первом релизе (далее целимся в `<= 5%`).
- Доля hard-связей в разумном диапазоне (ориентир: `10–30%`, без тотальной блокировки графа).
- На валидационном наборе тем: снижение «ложных блокировок» относительно baseline.
- Нет регрессии p95 latency roadmap.
### 3.9 Критерии завершения

- [ ] Все 221 PREREQ-рёбер имеют `weight` property
- [ ] `plan_route` использует `_compute_readiness` вместо бинарной проверки
- [ ] API roadmap возвращает `readiness`, `is_unlocked`, `blocking_prereqs`
- [ ] Integrity check валидирует weight ∈ [0, 1] при commit
- [ ] Frontend показывает readiness как прогресс-бар (а не замок/разблокировано)
- [ ] `still_default` для `PREREQ.weight=0.5` снижен до целевого порога релиза
- [ ] `prereq_weights_v1.csv` и отчёт покрытия закреплены как обязательные артефакты релиза

---

## 4. P2 — Misconception Nodes

### 4.1 Проблема

Текущая система не хранит информацию о **типичных ошибках** учеников. Когда ученик даёт неправильный ответ, система знает только «неправильно» — но не «какую именно ошибку он допустил» и «как её исправить».

Примеры типичных ошибок (misconceptions):
- «0.1 + 0.2 = 0.3 точно» (дроби vs числа с плавающей точкой — но в школьном контексте: «0.1 + 0.2 = 0.12», конкатенация вместо сложения)
- «-2² = 4» (неверный приоритет: минус vs возведение в степень)
- «√(a² + b²) = a + b» (неверное упрощение корня суммы)
- «sin(α + β) = sin α + sin β» (линейность, которой нет)

### 4.2 Модель данных

#### 4.2.1 Новый тип узла: Misconception

```
(:Misconception {
    uid: String,             // "MISC-KORENY-SUMMA-RAZLOZHENIE"
    tenant_id: String,
    title: String,           // "Корень суммы ≠ сумма корней"
    description: String,     // "Ученик считает, что √(a²+b²) = a+b"
    wrong_pattern: String,   // "√(X+Y) → √X + √Y"
    correct_pattern: String, // "√(a²+b²) — не упрощается без дополнительных условий"
    frequency: String,       // "high" | "medium" | "low"
    grade_range_min: Integer,
    grade_range_max: Integer,
    trigger_keywords: [String],  // ["корень суммы", "√(a²+b²)"]
    lifecycle_status: String,
    created_at: DateTime
})
```

#### 4.2.2 Новые типы связей

```
(:Misconception)-[:COMMON_IN]->(:Topic)
// "Эта ошибка часто встречается при изучении данной темы"

(:Misconception)-[:RESOLVED_BY]->(:Method)
// "Этот метод решения помогает преодолеть ошибку"

(:Misconception)-[:INDICATES_GAP_IN]->(:Skill)
// "Ошибка сигнализирует о пробеле в этом навыке"

(:Misconception)-[:CONTRADICTS]->(:Misconception)
// "Эти ошибки взаимоисключающие (разные модели мышления)"
```

#### 4.2.3 Полная схема связей Misconception

```
                    ┌──────────────┐
                    │  Topic       │
                    └──────┬───────┘
                           │ COMMON_IN
                    ┌──────▼───────┐
                    │ Misconception│
                    └──┬───┬───┬──┘
           RESOLVED_BY │   │   │ INDICATES_GAP_IN
                ┌──────▼┐  │  ┌▼──────┐
                │ Method │  │  │ Skill │
                └───────┘  │  └───────┘
                  CONTRADICTS
                    ┌──▼───────────┐
                    │ Misconception │
                    └──────────────┘
```

### 4.3 Canonical spec — обновления

Файл: `backend/app/core/canonical.py`

```python
# Добавить в ALLOWED_NODE_LABELS:
ALLOWED_NODE_LABELS = {
    ...,
    "Misconception",
}

# Добавить в ALLOWED_EDGE_TYPES:
ALLOWED_EDGE_TYPES = {
    ...,
    "COMMON_IN",
    "RESOLVED_BY",
    "INDICATES_GAP_IN",
    "CONTRADICTS",
}
```

### 4.4 Детектор ошибок

Новый модуль: `backend/app/services/misconception/detector.py`

```python
"""
MisconceptionDetector — анализирует неправильный ответ ученика
и определяет, какая именно misconception привела к ошибке.

Стратегия обнаружения (от дешёвой к дорогой):

1. Pattern matching — regex на wrong_pattern
2. Keyword matching — trigger_keywords в тексте ответа
3. LLM classification — если паттерны не сработали
"""
from dataclasses import dataclass


@dataclass
class DetectionResult:
    misconception_uid: str | None
    confidence: float  # 0.0–1.0
    detection_method: str  # "pattern" | "keyword" | "llm"
    suggested_method_uids: list[str]  # Method-ы для исправления


class MisconceptionDetector:

    def __init__(self, neo4j_repo, llm_service=None):
        self._repo = neo4j_repo
        self._llm = llm_service
        self._cache = {}  # topic_uid → list[Misconception]

    async def detect(
        self,
        topic_uid: str,
        student_answer: str,
        correct_answer: str,
        tenant_id: str = "default",
    ) -> DetectionResult | None:
        """
        Пытается определить misconception по ответу ученика.
        Возвращает None если ответ просто неправильный без характерного паттерна.
        """
        misconceptions = await self._get_misconceptions_for_topic(topic_uid, tenant_id)

        # Уровень 1: Pattern matching
        for m in misconceptions:
            if m.get("wrong_pattern") and self._matches_pattern(
                student_answer, m["wrong_pattern"]
            ):
                methods = await self._get_resolving_methods(m["uid"], tenant_id)
                return DetectionResult(
                    misconception_uid=m["uid"],
                    confidence=0.9,
                    detection_method="pattern",
                    suggested_method_uids=methods,
                )

        # Уровень 2: Keyword matching
        for m in misconceptions:
            keywords = m.get("trigger_keywords", [])
            if keywords and any(kw.lower() in student_answer.lower() for kw in keywords):
                methods = await self._get_resolving_methods(m["uid"], tenant_id)
                return DetectionResult(
                    misconception_uid=m["uid"],
                    confidence=0.6,
                    detection_method="keyword",
                    suggested_method_uids=methods,
                )

        # Уровень 3: LLM classification (только если есть LLM-сервис)
        if self._llm and misconceptions:
            result = await self._llm_classify(
                student_answer, correct_answer, misconceptions
            )
            if result:
                return result

        return None

    async def _get_misconceptions_for_topic(
        self, topic_uid: str, tenant_id: str
    ) -> list[dict]:
        if topic_uid in self._cache:
            return self._cache[topic_uid]

        query = """
        MATCH (m:Misconception)-[:COMMON_IN]->(t:Topic {uid: $topic_uid})
        WHERE m.tenant_id = $tenant_id AND m.lifecycle_status = 'ACTIVE'
        RETURN m {.*} AS misconception
        ORDER BY m.frequency DESC
        """
        records = await self._repo.read(query, {
            "topic_uid": topic_uid,
            "tenant_id": tenant_id,
        })
        result = [r["misconception"] for r in records]
        self._cache[topic_uid] = result
        return result

    async def _get_resolving_methods(
        self, misconception_uid: str, tenant_id: str
    ) -> list[str]:
        query = """
        MATCH (m:Misconception {uid: $uid})-[:RESOLVED_BY]->(method:Method)
        WHERE method.tenant_id = $tenant_id
        RETURN method.uid AS uid
        """
        records = await self._repo.read(query, {
            "uid": misconception_uid,
            "tenant_id": tenant_id,
        })
        return [r["uid"] for r in records]

    @staticmethod
    def _matches_pattern(answer: str, pattern: str) -> bool:
        """Простое сопоставление паттерна с ответом."""
        # Нормализуем: убираем пробелы, приводим к нижнему регистру
        normalized = answer.lower().replace(" ", "")
        pattern_normalized = pattern.lower().replace(" ", "")
        return pattern_normalized in normalized

    async def _llm_classify(
        self,
        student_answer: str,
        correct_answer: str,
        misconceptions: list[dict],
    ) -> DetectionResult | None:
        """Использует LLM для классификации ошибки."""
        prompt = (
            f"Ответ ученика: {student_answer}\n"
            f"Правильный ответ: {correct_answer}\n\n"
            "Определи, какая из следующих типичных ошибок лучше всего "
            "описывает ошибку ученика:\n"
        )
        for i, m in enumerate(misconceptions, 1):
            prompt += f"{i}. {m['title']}: {m.get('description', '')}\n"
        prompt += "\nЕсли ни одна не подходит, ответь 'none'."

        # LLM call (simplified, actual implementation depends on llm_service API)
        response = await self._llm.generate(prompt, max_tokens=50)
        # Parse response to find matching misconception index
        # ... (implementation details)
        return None  # Fallback
```

### 4.5 Интеграция с check_answer

Файл: `backend/app/domain/services/api_services/lesson_stage_service.py`

В функции `check_answer`, после определения что ответ неверный:

```python
# После определения is_correct = False:
detector = MisconceptionDetector(neo4j_repo=self._kb_repo)
detection = await detector.detect(
    topic_uid=current_topic_uid,
    student_answer=student_answer,
    correct_answer=correct_answer,
    tenant_id=tenant_id,
)

if detection and detection.confidence >= 0.6:
    # Добавить в ответ информацию о misconception
    response["misconception"] = {
        "uid": detection.misconception_uid,
        "confidence": detection.confidence,
        "suggested_methods": detection.suggested_method_uids,
    }
    # Записать в telemetry для data-driven весов
    await self._emit_telemetry("misconception_detected", {
        "topic_uid": current_topic_uid,
        "misconception_uid": detection.misconception_uid,
        "confidence": detection.confidence,
        "student_class": user_class,
    })
```

### 4.6 Начальный набор Misconception-ов

Скрипт seed: `backend/scripts/seed_misconceptions.py`

Категории для первой итерации (по частотности в школьной математике):

| Тема | Misconception | wrong_pattern | frequency |
|------|--------------|---------------|-----------|
| Дроби | `a/b + c/d = (a+c)/(b+d)` | `X/Y+Z/W → (X+Z)/(Y+W)` | high |
| Степени | `-a² = (-a)²` | `-X^2 → X^2` | high |
| Корни | `√(a+b) = √a + √b` | `√(X+Y) → √X+√Y` | high |
| Логарифмы | `log(a+b) = log(a) + log(b)` | `log(X+Y) → logX+logY` | medium |
| Тригонометрия | `sin(α+β) = sinα + sinβ` | `sin(X+Y) → sinX+sinY` | high |
| Уравнения | Деление на 0 при решении | — | medium |
| Неравенства | Не меняет знак при делении на отрицательное | — | high |
| Проценты | `a% от b ≠ b% от a` (ученик думает что разные) | — | low |

### 4.7 Критерии завершения

- [ ] `Misconception` добавлен в `ALLOWED_NODE_LABELS`
- [ ] `COMMON_IN`, `RESOLVED_BY`, `INDICATES_GAP_IN`, `CONTRADICTS` добавлены в `ALLOWED_EDGE_TYPES`
- [ ] Seed-скрипт создаёт ≥20 базовых misconceptions с привязкой к Topic и Method
- [ ] `MisconceptionDetector` интегрирован в `check_answer`
- [ ] API возвращает `misconception` объект в ответе при обнаружении
- [ ] Telemetry записывает детекции для будущей аналитики

---

## 5. P3 — Skill Composition Graph

### 5.1 Проблема

Текущие Skill-узлы изолированы — каждый связан только «вверх» (REQUIRES_SKILL от Topic) и «вниз» (HAS_METHOD к Method). Навыки между собой не связаны.

В реальности навыки **компонуются**:
- «Подстановка переменных» + «Решение линейных уравнений» → «Решение систем подстановкой»
- «Вычисление производной» + «Нахождение нулей функции» → «Нахождение экстремумов»

Без этой информации система не может:
- Показать ученику «skill tree» (дерево навыков) — мощнейший мотиватор
- Предсказать, какие навыки ученик «почти» разблокировал
- Рекомендовать оптимальный следующий навык для максимального прогресса

### 5.2 Модель данных

#### 5.2.1 Новый тип связи: COMPOSES

```
(:Skill)-[:COMPOSES {
    role: String,           // "primary" | "secondary" | "auxiliary"
    contribution: Float     // 0.0–1.0, вклад навыка в композитный
}]->(:Skill)
```

Связь читается: «Skill A **входит в состав** Skill B (с ролью role и вкладом contribution)».

#### 5.2.2 Направление

```
(:Skill {title: "Подстановка"})
    -[:COMPOSES {role: "primary", contribution: 0.6}]->
(:Skill {title: "Решение систем подстановкой"})

(:Skill {title: "Линейные уравнения"})
    -[:COMPOSES {role: "secondary", contribution: 0.4}]->
(:Skill {title: "Решение систем подстановкой"})
```

Composition graph — это **DAG**: циклы запрещены (навык не может входить в состав себя транзитивно).

#### 5.2.3 Computed Properties на Skill

Новые свойства, вычисляемые при build/seed:

```
(:Skill {
    ...,
    composition_depth: Integer,  // 0 = атомарный навык, 1+ = композитный
    component_count: Integer,    // сколько навыков входят в состав (прямых)
    is_atomic: Boolean           // true если ни один навык не COMPOSES в него
})
```

### 5.3 Canonical spec — обновления

```python
ALLOWED_EDGE_TYPES = {
    ...,
    "COMPOSES",
}
```

### 5.4 Integrity checks

Файл: `backend/app/services/integrity.py`

```python
def check_skill_composition_cycles(rels: list[dict]) -> list[tuple[str, str]]:
    """Проверяет, что COMPOSES-граф ацикличен."""
    import networkx as nx

    G = nx.DiGraph()
    for rel in rels:
        if rel.get("type") == "COMPOSES":
            G.add_edge(rel["from_uid"], rel["to_uid"])

    cycles = list(nx.simple_cycles(G))
    return [(c[0], c[-1]) for c in cycles]


def check_composes_contributions(rels: list[dict]) -> list[str]:
    """
    Проверяет, что сумма contribution для каждого целевого Skill ≤ 1.0.
    """
    from collections import defaultdict

    targets = defaultdict(float)
    violations = []
    for rel in rels:
        if rel.get("type") == "COMPOSES":
            c = rel.get("properties", {}).get("contribution", 0.0)
            targets[rel["to_uid"]] += c

    for uid, total in targets.items():
        if total > 1.05:  # 5% tolerance
            violations.append(f"Skill {uid}: total contribution={total:.2f} > 1.0")

    return violations
```

### 5.5 Skill Tree для фронтенда

#### 5.5.1 Новый API endpoint

`GET /v1/engine/skill-tree?topic_uid=X&depth=3`

```json
{
  "root_skills": [
    {
      "uid": "SK-RESHENIE-SISTEM-PODST",
      "title": "Решение систем подстановкой",
      "mastery": 0.3,
      "is_atomic": false,
      "components": [
        {
          "uid": "SK-PODSTANOVKA",
          "title": "Подстановка переменных",
          "mastery": 0.8,
          "role": "primary",
          "contribution": 0.6,
          "is_atomic": true,
          "components": []
        },
        {
          "uid": "SK-LINEJNYE-URAVNENIYA",
          "title": "Решение линейных уравнений",
          "mastery": 0.9,
          "role": "secondary",
          "contribution": 0.4,
          "is_atomic": true,
          "components": []
        }
      ]
    }
  ]
}
```

#### 5.5.2 Cypher-запрос

```cypher
MATCH (t:Topic {uid: $topic_uid})-[:REQUIRES_SKILL]->(sk:Skill)
WHERE t.tenant_id = $tenant_id
OPTIONAL MATCH (component:Skill)-[c:COMPOSES]->(sk)
RETURN sk.uid AS skill_uid,
       sk.title AS skill_title,
       sk.is_atomic AS is_atomic,
       collect({
           uid: component.uid,
           title: component.title,
           role: c.role,
           contribution: c.contribution,
           mastery: component.mastery
       }) AS components
```

### 5.6 Predicted Mastery для композитных навыков

Если ученик ещё не проверялся по композитному навыку, его mastery можно **предсказать** на основе компонентов:

```python
def predict_composite_mastery(
    components: list[dict],  # [{uid, mastery, contribution}, ...]
) -> float:
    """
    Предсказанный mastery композитного навыка =
    взвешенное среднее mastery компонентов с penalty за неполноту.
    """
    if not components:
        return 0.0

    total_contribution = sum(c["contribution"] for c in components)
    weighted_sum = sum(c["contribution"] * c["mastery"] for c in components)

    base = weighted_sum / total_contribution if total_contribution > 0 else 0.0

    # Penalty: если какой-то компонент ниже 0.3, это сильно мешает
    min_mastery = min(c["mastery"] for c in components)
    penalty = max(0, 0.3 - min_mastery) * 0.5

    return max(0.0, base - penalty)
```

### 5.7 Визуализация (фронтенд)

Skill tree рендерится как **RPG-style skill tree**:
- Атомарные навыки — маленькие круги внизу
- Композитные навыки — большие круги выше, соединены линиями с компонентами
- Цвет: серый (locked), жёлтый (in progress, 0.1–0.49), зелёный (proficient, 0.5–0.89), золотой (mastered, 0.9+)
- При наведении — tooltip с mastery каждого компонента
- Кликабельно: переход к методам и примерам навыка

### 5.8 Критерии завершения

- [ ] `COMPOSES` добавлен в `ALLOWED_EDGE_TYPES`
- [ ] Integrity check на циклы в COMPOSES-графе
- [ ] Integrity check на сумму contribution ≤ 1.0
- [ ] API `GET /v1/engine/skill-tree` работает
- [ ] `predict_composite_mastery` используется в roadmap при отсутствии прямого mastery
- [ ] Seed-скрипт создаёт ≥30 COMPOSES-связей для ключевых навыков алгебры

---

## 6. P4 — Neo4j Vector Index (замена Qdrant)

### 6.1 Проблема

Текущая архитектура использует **два отдельных хранилища** для связанных данных:
- **Neo4j** — граф (узлы, рёбра, свойства)
- **Qdrant** — vector embeddings для semantic search (коллекция `concepts`, 1536-dim)

Это создаёт:
1. **Двойную синхронизацию**: при `graph.committed` нужен отдельный worker для переиндексации в Qdrant
2. **Расхождение данных**: embedding в Qdrant может отстать от Neo4j (race condition, падение worker-а)
3. **Невозможность гибридных запросов**: нельзя в одном запросе найти «семантически похожие узлы» И обойти их PREREQ-граф
4. **Лишний сервис**: Qdrant — отдельный процесс, потребляющий RAM и CPU

### 6.2 Решение: Neo4j Vector Index

Neo4j с версии 5.11 поддерживает **нативные vector indexes** (ANN — approximate nearest neighbor search). Текущая версия проекта: Neo4j 5.26 — полная поддержка.

### 6.3 Миграция

#### 6.3.1 Шаг 1: Создание vector index в Neo4j

```cypher
// Создать vector index на embedding свойстве
CREATE VECTOR INDEX concept_embeddings IF NOT EXISTS
FOR (n:Concept)
ON (n.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
}
```

```cypher
// Индексы для других типов узлов
CREATE VECTOR INDEX method_embeddings IF NOT EXISTS
FOR (n:Method) ON (n.embedding)
OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}

CREATE VECTOR INDEX example_embeddings IF NOT EXISTS
FOR (n:Example) ON (n.embedding)
OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}

CREATE VECTOR INDEX topic_embeddings IF NOT EXISTS
FOR (n:Topic) ON (n.embedding)
OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}
```

#### 6.3.2 Шаг 2: Перенос embeddings из Qdrant в Neo4j

Скрипт: `backend/scripts/migrate_qdrant_to_neo4j.py`

```python
"""
Миграция vector embeddings из Qdrant в Neo4j.

1. Читает все точки из Qdrant коллекции 'concepts'
2. Для каждой точки находит соответствующий узел в Neo4j по uid
3. Записывает embedding как свойство узла
"""
import asyncio
from qdrant_client import QdrantClient
from neo4j import AsyncGraphDatabase


async def migrate():
    qdrant = QdrantClient(url="http://localhost:6333")
    neo4j_driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "neo4j-password"),
    )

    # Считать все точки из Qdrant
    offset = None
    batch_size = 500
    total = 0

    while True:
        points, offset = qdrant.scroll(
            collection_name="concepts",
            limit=batch_size,
            offset=offset,
            with_vectors=True,
        )

        if not points:
            break

        # Записать в Neo4j одним запросом на батч (быстрее и стабильнее)
        rows = []
        for point in points:
            uid = point.payload.get("uid") or point.id
            embedding = point.vector
            rows.append({"uid": uid, "embedding": embedding})

        async with neo4j_driver.session() as session:
            result = await session.run(
                """
                UNWIND $rows AS row
                MATCH (n {uid: row.uid, tenant_id: 'default'})
                SET n.embedding = row.embedding
                RETURN count(n) AS updated
                """,
                rows=rows,
            )
            record = await result.single()
            total += int(record["updated"])

        if offset is None:
            break

    print(f"Migrated {total} embeddings from Qdrant to Neo4j")

    # Verify
    async with neo4j_driver.session() as session:
        result = await session.run(
            "MATCH (n) WHERE n.embedding IS NOT NULL RETURN count(n) AS cnt"
        )
        record = await result.single()
        print(f"Nodes with embeddings in Neo4j: {record['cnt']}")

    await neo4j_driver.close()


asyncio.run(migrate())
```

#### 6.3.3 Шаг 3: Замена QdrantService на Neo4jVectorService

Новый файл: `backend/app/services/vector/neo4j_vector_service.py`

```python
"""
Neo4j Vector Service — замена QdrantService.
Использует нативные vector indexes Neo4j 5.11+.
"""
from typing import Optional


class Neo4jVectorService:

    def __init__(self, neo4j_repo):
        self._repo = neo4j_repo

    async def upsert_embedding(
        self,
        uid: str,
        embedding: list[float],
        tenant_id: str = "default",
    ) -> None:
        """Записать embedding в свойство узла."""
        await self._repo.write(
            """
            MATCH (n {uid: $uid, tenant_id: $tenant_id})
            SET n.embedding = $embedding
            """,
            {"uid": uid, "embedding": embedding, "tenant_id": tenant_id},
        )

    async def query_similar(
        self,
        embedding: list[float],
        top_k: int = 5,
        label: Optional[str] = None,
        tenant_id: str = "default",
    ) -> list[dict]:
        """Найти семантически похожие узлы."""
        index_name = f"{label.lower()}_embeddings" if label else "concept_embeddings"

        records = await self._repo.read(
            f"""
            CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
            YIELD node, score
            WHERE node.tenant_id = $tenant_id
            RETURN node.uid AS uid,
                   node.title AS title,
                   labels(node)[0] AS label,
                   score
            ORDER BY score DESC
            """,
            {
                "index_name": index_name,
                "top_k": top_k,
                "embedding": embedding,
                "tenant_id": tenant_id,
            },
        )
        return [dict(r) for r in records]

    async def hybrid_search(
        self,
        embedding: list[float],
        top_k: int = 5,
        graph_depth: int = 2,
        tenant_id: str = "default",
    ) -> list[dict]:
        """
        Гибридный запрос: семантический поиск + graph traversal.
        Находит похожие узлы И их соседей по графу.
        """
        records = await self._repo.read(
            """
            CALL db.index.vector.queryNodes('concept_embeddings', $top_k, $embedding)
            YIELD node, score
            WHERE node.tenant_id = $tenant_id
            WITH node, score
            OPTIONAL MATCH path = (node)-[*1..$depth]-(neighbor)
            WHERE neighbor.tenant_id = $tenant_id
            RETURN node.uid AS source_uid,
                   node.title AS source_title,
                   score AS similarity,
                   collect(DISTINCT {
                       uid: neighbor.uid,
                       title: neighbor.title,
                       label: labels(neighbor)[0],
                       distance: length(path)
                   }) AS neighbors
            ORDER BY score DESC
            """,
            {
                "top_k": top_k,
                "embedding": embedding,
                "tenant_id": tenant_id,
                "depth": graph_depth,
            },
        )
        return [dict(r) for r in records]
```

### 6.4 Гибридные запросы — ключевое преимущество

#### 6.4.1 «Найди похожую тему и покажи путь до неё»

```cypher
// Ученик спрашивает: "как решать уравнения с корнями"
// → embedding запроса → vector search → graph path
CALL db.index.vector.queryNodes('topic_embeddings', 3, $query_embedding)
YIELD node AS target, score
WHERE target.tenant_id = $tenant_id

// Найти путь от текущей темы ученика до найденной
MATCH path = shortestPath(
    (current:Topic {uid: $current_topic_uid})-[:PREREQ*..10]->(target)
)
RETURN target.uid, target.title, score, [n IN nodes(path) | n.title] AS learning_path
```

#### 6.4.2 «Найди метод, похожий на описание, и покажи его в контексте»

```cypher
CALL db.index.vector.queryNodes('method_embeddings', 5, $query_embedding)
YIELD node AS method, score

MATCH (skill:Skill)-[:HAS_METHOD]->(method)
MATCH (topic:Topic)-[:REQUIRES_SKILL]->(skill)
MATCH (method)-[:HAS_EXAMPLE]->(ex:Example)

RETURN method.uid, method.title, score,
       skill.title AS skill_name,
       topic.title AS topic_name,
       collect(ex.title)[..3] AS example_titles
ORDER BY score DESC
```

### 6.5 Удаление Qdrant из инфраструктуры

#### 6.5.1 docker-compose.infra.yml

Удалить сервис `qdrant` из `docker/docker-compose.infra.yml`.

#### 6.5.2 Код

- Удалить: `backend/app/services/vector/qdrant_service.py`
- Заменить все импорты `QdrantService` на `Neo4jVectorService`
- Удалить `qdrant-client` из `requirements.txt`
- Обновить `backend/app/services/vector/indexer.py`: вместо Qdrant upsert — Neo4j SET embedding

#### 6.5.3 Vector sync worker

Упрощается: вместо «прочитать из Neo4j → вычислить embedding → записать в Qdrant» становится «прочитать узел → вычислить embedding → SET embedding на том же узле в Neo4j».

### 6.6 Оценка производительности

| Операция | Qdrant (текущее) | Neo4j Vector Index |
|----------|------------------|--------------------|
| Vector search (top-5 из 6K) | ~2ms | ~5ms |
| Hybrid (vector + 2-hop graph) | ~2ms + ~15ms (2 запроса) | ~8ms (1 запрос) |
| Upsert embedding | ~1ms (HTTP) | ~3ms (Bolt, тот же узел) |
| Инфраструктура | Отдельный процесс, ~200MB RAM | Уже есть (Neo4j) |

Для масштаба 6K узлов разница незначительна. Neo4j vector index оптимизирован для <100K vectors. При >1M vectors Qdrant может быть быстрее, но для образовательного контента это недостижимый масштаб.

### 6.7 Fallback-стратегия

Если Neo4j vector index окажется недостаточно быстрым при росте:
- Оставить Qdrant как read-replica для чисто-векторных запросов
- Гибридные запросы (vector + graph) всегда в Neo4j

### 6.8 Критерии завершения

- [ ] Vector indexes созданы для Topic, Method, Example, Concept
- [ ] Все embeddings перенесены из Qdrant в Neo4j (свойство `embedding`)
- [ ] `Neo4jVectorService` заменяет `QdrantService` во всех точках
- [ ] `hybrid_search` работает (vector + graph traversal в одном запросе)
- [ ] Qdrant удалён из `docker-compose.infra.yml`
- [ ] `qdrant-client` удалён из `requirements.txt`
- [ ] Latency hybrid search ≤ 20ms (p95) при текущем масштабе

---

## 7. P5 — Learner State Layer (PostgreSQL-first)

### 7.1 Проблема

Текущее хранение прогресса ученика — **плоский dict** в PostgreSQL: `{topic_uid: mastery_float}`. Это не позволяет:

1. **Graph-based recommendations**: «ученики с похожим паттерном ошибок прошли тему X после метода Y»
2. **Trajectory analysis**: как ученик двигался по графу знаний (sequence of topics)
3. **Forgetting curve**: когда ученик последний раз практиковал навык (spaced repetition)
4. **Social learning**: паттерны группы (класс, школа)
5. **Misconception clustering**: группировка учеников по типам ошибок

### 7.2 Архитектурное решение

Источник истины для learner-state — **PostgreSQL StudyNinja**.  
Neo4j содержит только **статический граф знаний** и его контентные связи.

```
Neo4j (static):
  Subject → Section → Subsection → Topic → Skill → Method → Example
  + контентные расширения (PREREQ weight, Bloom, DifficultyTier, ...)

PostgreSQL (dynamic user state):
  user_topic_state
  user_skill_state
  user_example_attempts
  user_misconception_state
  user_prereq_weights
  user_tier_state (для P8)
```

Плюсы:
- нет дублирования логики состояния между БД;
- проще транзакционность в учебном флоу (check_answer и обновление прогресса);
- P8 и персональные веса естественно живут рядом с остальным user-state.

### 7.3 Модель данных (PostgreSQL)

#### 7.3.1 Таблицы состояния

```sql
-- Текущее состояние темы
CREATE TABLE user_topic_state (
  tenant_id TEXT NOT NULL DEFAULT 'default',
  user_uid TEXT NOT NULL,
  topic_uid TEXT NOT NULL,
  mastery DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  status TEXT NOT NULL DEFAULT 'not_started', -- not_started|in_progress|completed|reviewing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, user_uid, topic_uid)
);

-- Текущее состояние навыка
CREATE TABLE user_skill_state (
  tenant_id TEXT NOT NULL DEFAULT 'default',
  user_uid TEXT NOT NULL,
  skill_uid TEXT NOT NULL,
  score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  tier TEXT NOT NULL DEFAULT 'novice',
  last_practiced TIMESTAMPTZ,
  practice_count INTEGER NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, user_uid, skill_uid)
);

-- История попыток по примерам
CREATE TABLE user_example_attempts (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'default',
  user_uid TEXT NOT NULL,
  example_uid TEXT NOT NULL,
  result TEXT NOT NULL, -- correct|incorrect|partial|skipped
  time_spent_sec INTEGER,
  misconception_uid TEXT,
  attempt_number INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Агрегат по misconceptions
CREATE TABLE user_misconception_state (
  tenant_id TEXT NOT NULL DEFAULT 'default',
  user_uid TEXT NOT NULL,
  misconception_uid TEXT NOT NULL,
  occurrence_count INTEGER NOT NULL DEFAULT 0,
  first_seen TIMESTAMPTZ,
  last_seen TIMESTAMPTZ,
  resolved BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (tenant_id, user_uid, misconception_uid)
);
```

### 7.4 Ключевые запросы (PG + Neo4j)

#### 7.4.1 Collaborative filtering — «похожие ученики»

```sql
-- 1) Найти пользователей с похожим профилем misconceptions
WITH my_m AS (
  SELECT misconception_uid
  FROM user_misconception_state
  WHERE tenant_id = $1 AND user_uid = $2
),
similar AS (
  SELECT ums.user_uid, count(*) AS shared_misconceptions
  FROM user_misconception_state ums
  JOIN my_m ON my_m.misconception_uid = ums.misconception_uid
  WHERE ums.tenant_id = $1 AND ums.user_uid <> $2
  GROUP BY ums.user_uid
  ORDER BY shared_misconceptions DESC
  LIMIT 10
)
SELECT * FROM similar;

-- 2) По similar users собрать topic_uid completed и резолвить title в Neo4j отдельным read-запросом.
```

#### 7.4.2 Spaced repetition — «что пора повторить»

```sql
SELECT skill_uid, score, last_practiced
FROM user_skill_state
WHERE tenant_id = $1
  AND user_uid = $2
  AND last_practiced < now() - make_interval(days => $3)
  AND score < 0.9
ORDER BY last_practiced ASC
LIMIT 10;

-- titles для skill_uid подтягиваются из Neo4j (батч-resolve).
```

#### 7.4.3 Learning trajectory — «путь ученика по графу»

```sql
SELECT topic_uid, status, mastery, started_at, completed_at
FROM user_topic_state
WHERE tenant_id = $1
  AND user_uid = $2
  AND status IN ('completed', 'in_progress')
ORDER BY started_at NULLS LAST;

-- PREREQ-контекст для этих topic_uid подтягивается из Neo4j.
```

#### 7.4.4 Class analytics — «аналитика по классу»

```sql
-- Агрегация по unresolved misconceptions пользователей нужного класса
SELECT ums.misconception_uid, count(DISTINCT ums.user_uid) AS struggling_students
FROM user_misconception_state ums
JOIN users u ON u.uid = ums.user_uid
WHERE ums.tenant_id = $1
  AND u.user_class = $2
  AND ums.resolved = FALSE
GROUP BY ums.misconception_uid
ORDER BY struggling_students DESC
LIMIT 50;

-- Затем через Neo4j: Misconception -> COMMON_IN -> Topic для итоговой витрины.
```

### 7.5 Запись событий

#### 7.5.1 Event-driven обновление learner-state в PostgreSQL

При каждом `check_answer` в StudyNinja-API:

```python
# В lesson_stage_service.py, после mastery_update:
async def _update_learner_state(
    self,
    user_uid: str,
    example_uid: str,
    result: str,
    time_spent: int,
    misconception_uid: str | None,
    topic_uid: str,
    skill_uid: str,
    new_mastery: float,
):
    """Обновить user_topic_state / user_skill_state / attempts / misconception_state в PostgreSQL."""
    # 1. append attempt in user_example_attempts
    await self._pg_repo.insert_example_attempt(...)

    # 2. upsert user_skill_state
    await self._pg_repo.upsert_skill_state(...)

    # 3. upsert user_topic_state
    await self._pg_repo.upsert_topic_state(...)

    # 4. upsert user_misconception_state (если есть)
    if misconception_uid:
        await self._pg_repo.upsert_misconception_state(...)
```

### 7.6 Privacy и разделение данных

- Персональные данные и learner-state хранятся в PostgreSQL StudyNinja-API
- Neo4j не хранит per-user state (нет дублирования и рассинхрона)
- При удалении аккаунта → каскадное удаление строк пользователя в PG-таблицах состояния
- GDPR compliance: удаление user-state выполняется в PostgreSQL-транзакции

### 7.7 Критерии завершения

- [ ] `user_topic_state`, `user_skill_state`, `user_example_attempts`, `user_misconception_state` обновляются при каждом событии
- [ ] Collaborative filtering endpoint: `GET /v1/engine/recommendations?user_uid=X`
- [ ] Spaced repetition endpoint: `GET /v1/engine/review-queue?user_uid=X`
- [ ] Class analytics endpoint: `GET /v1/engine/class-analytics?user_class=7`
- [ ] Cascade delete learner-state при удалении аккаунта

---

## 8. P6 — Bloom's Taxonomy Levels

### 8.1 Проблема

Все Example и Method сейчас дифференцированы только по `difficulty_level` (числовая сложность 1–10). Нет разделения по **когнитивному уровню** — типу мыслительной операции, которую требует задание.

Таксономия Блума определяет 6 уровней когнитивных операций (от простого к сложному):

| Уровень | Название | Описание | Пример в математике |
|---------|----------|----------|---------------------|
| 1 | **Remember** (Запоминание) | Воспроизвести факт | «Чему равен sin(90°)?» |
| 2 | **Understand** (Понимание) | Объяснить своими словами | «Почему sin(90°) = 1?» |
| 3 | **Apply** (Применение) | Использовать в знакомой ситуации | «Найдите sin(90°) в задаче о высоте» |
| 4 | **Analyze** (Анализ) | Разобрать на составные части | «Определите, какая тригонометрическая функция нужна» |
| 5 | **Evaluate** (Оценка) | Оценить решение | «Проверьте, верно ли решение ученика» |
| 6 | **Create** (Создание) | Построить новое решение | «Придумайте задачу на синус» |

### 8.2 Модель данных

#### 8.2.1 Новый тип узла: LearningObjective

```
(:LearningObjective {
    uid: String,                 // "LO-TOPIC_UID-BLOOM_LEVEL"
    tenant_id: String,
    topic_uid: String,           // К какой теме относится
    bloom_level: Integer,        // 1–6
    bloom_label: String,         // "remember" | "understand" | "apply" | "analyze" | "evaluate" | "create"
    description: String,         // "Ученик может воспроизвести формулу синуса"
    success_criteria: String,    // "Правильно назвать значения sin для стандартных углов"
    lifecycle_status: String,
    created_at: DateTime
})
```

#### 8.2.2 Новые связи

```
(:Topic)-[:HAS_OBJECTIVE]->(:LearningObjective)
// "Тема имеет цель обучения на определённом когнитивном уровне"

(:LearningObjective)-[:ASSESSED_BY]->(:Example)
// "Эта цель проверяется данным примером"

(:LearningObjective)-[:TAUGHT_BY]->(:Method)
// "Эта цель достигается данным методом"
```

#### 8.2.3 Обновление Example и Method

Добавить свойство на существующие узлы:

```
(:Example {
    ...,
    bloom_level: Integer    // 1–6
})

(:Method {
    ...,
    bloom_level: Integer    // 1–6
})
```

### 8.3 Canonical spec — обновления

```python
ALLOWED_NODE_LABELS = {
    ...,
    "LearningObjective",
}

ALLOWED_EDGE_TYPES = {
    ...,
    "HAS_OBJECTIVE",
    "ASSESSED_BY",
    "TAUGHT_BY",
}
```

### 8.4 Adaptive Engine — использование Bloom

#### 8.4.1 Прогрессия по уровням

Для каждой темы ученик проходит уровни последовательно:

```python
BLOOM_PROGRESSION = {
    1: {"name": "remember", "mastery_threshold": 0.7, "min_examples": 2},
    2: {"name": "understand", "mastery_threshold": 0.6, "min_examples": 2},
    3: {"name": "apply", "mastery_threshold": 0.6, "min_examples": 3},
    4: {"name": "analyze", "mastery_threshold": 0.5, "min_examples": 2},
    5: {"name": "evaluate", "mastery_threshold": 0.5, "min_examples": 1},
    6: {"name": "create", "mastery_threshold": 0.4, "min_examples": 1},
}


def get_current_bloom_level(
    topic_uid: str,
    user_attempts: list[dict],  # [{example_uid, bloom_level, result}, ...]
) -> int:
    """Определить текущий когнитивный уровень ученика по теме."""
    from collections import defaultdict

    level_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for attempt in user_attempts:
        bl = attempt.get("bloom_level", 1)
        level_stats[bl]["total"] += 1
        if attempt["result"] == "correct":
            level_stats[bl]["correct"] += 1

    current_level = 1
    for level in range(1, 7):
        config = BLOOM_PROGRESSION[level]
        stats = level_stats[level]
        if stats["total"] < config["min_examples"]:
            break
        mastery = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        if mastery >= config["mastery_threshold"]:
            current_level = level + 1
        else:
            break

    return min(current_level, 6)
```

#### 8.4.2 Выбор следующего примера

```cypher
// Выбрать Example подходящего когнитивного уровня
MATCH (t:Topic {uid: $topic_uid})-[:REQUIRES_SKILL]->(:Skill)-[:HAS_METHOD]->(:Method)-[:HAS_EXAMPLE]->(ex:Example)
WHERE ex.bloom_level = $target_bloom_level
  AND ex.difficulty_level BETWEEN $min_diff AND $max_diff
  AND NOT ex.uid IN $attempted_example_uids
RETURN ex
ORDER BY rand()
LIMIT 1
```

`attempted_example_uids` формируется из PostgreSQL (`user_example_attempts`) перед выполнением Cypher.

### 8.5 Миграция существующих данных

#### 8.5.1 Автоматическая классификация по заголовку/содержанию

```python
BLOOM_KEYWORDS = {
    1: ["назовите", "запишите", "перечислите", "сформулируйте", "вычислите"],
    2: ["объясните", "опишите", "сравните", "почему"],
    3: ["решите", "найдите", "вычислите", "примените", "используйте"],
    4: ["определите", "классифицируйте", "проанализируйте", "какой метод"],
    5: ["проверьте", "оцените", "верно ли", "докажите"],
    6: ["придумайте", "составьте", "предложите", "сконструируйте"],
}


def classify_bloom_level(title: str, statement: str) -> int:
    """Эвристическая классификация по ключевым словам."""
    text = f"{title} {statement}".lower()
    # Проверяем от высшего уровня к низшему (более специфичные слова)
    for level in range(6, 0, -1):
        for keyword in BLOOM_KEYWORDS[level]:
            if keyword in text:
                return level
    return 3  # Default: Apply (самый частый)
```

#### 8.5.2 Массовая миграция

```cypher
// После запуска Python-скрипта, который классифицировал все Example:
UNWIND $classified AS item
MATCH (ex:Example {uid: item.uid})
SET ex.bloom_level = item.bloom_level
```

### 8.6 Критерии завершения

- [ ] `LearningObjective` добавлен в `ALLOWED_NODE_LABELS`
- [ ] `HAS_OBJECTIVE`, `ASSESSED_BY`, `TAUGHT_BY` добавлены в `ALLOWED_EDGE_TYPES`
- [ ] Все Example получили `bloom_level` (автоклассификация + ручная проверка)
- [ ] Adaptive engine учитывает bloom_level при выборе следующего задания
- [ ] API roadmap показывает прогресс по bloom-уровням для каждой темы

---

## 9. P7 — Multi-Subject Cross-Links

### 9.1 Проблема

Текущий граф содержит единственный Subject — «Mathematics». При расширении на Physics, Chemistry, Computer Science:

1. Нужны **кросс-предметные связи** (физика использует производную из математики)
2. Нужны **мета-узлы компетенций** для ФГОС / Bloom / 21st century skills
3. Необходима **изоляция** — преподаватель физики не должен редактировать граф математики

### 9.2 Модель данных

#### 9.2.1 Новый тип связи: USES_KNOWLEDGE

```
(:Topic {subject: "Physics", title: "Кинематика"})
  -[:USES_KNOWLEDGE {
      importance: Float,     // 0.0–1.0
      aspect: String,        // "computational" | "conceptual" | "notational"
      description: String    // "Использует производную для вычисления скорости"
  }]->
(:Topic {subject: "Mathematics", title: "Производная функции"})
```

#### 9.2.2 Новый тип узла: Competency (ФГОС-компетенции)

```
(:Competency {
    uid: String,              // "COMP-FGOS-MATH-MODEL"
    tenant_id: String,
    title: String,            // "Математическое моделирование"
    standard: String,         // "FGOS-2022" | "21CS" (21st Century Skills)
    level: String,            // "basic" | "advanced" | "proficient"
    description: String,
    lifecycle_status: String
})
```

#### 9.2.3 Связи Competency

```
(:Competency)-[:DEVELOPED_BY]->(:Topic)
// "Эта компетенция развивается при изучении данной темы"

(:Competency)-[:ASSESSED_IN]->(:LearningObjective)
// "Эта компетенция оценивается через данную учебную цель"

(:Competency)-[:REQUIRES_COMPETENCY]->(:Competency)
// "Для этой компетенции нужна другая" (иерархия ФГОС)
```

### 9.3 Изоляция предметов

#### 9.3.1 Свойство `subject` на Subject-узлах

```cypher
// Каждый Subject имеет уникальный код
(:Subject {uid: "MATH-FULL-V1", title: "Mathematics", subject_code: "MATH"})
(:Subject {uid: "PHYS-FULL-V1", title: "Physics", subject_code: "PHYS"})
```

#### 9.3.2 Каскадная фильтрация по предмету

Все запросы добавляют фильтр по subject при необходимости:

```cypher
// Roadmap только по математике
MATCH (subj:Subject {subject_code: $subject_code})-[:CONTAINS*1..3]->(t:Topic)
WHERE t.tenant_id = $tenant_id
...
```

#### 9.3.3 Permission model

В proposal system добавить проверку: автор proposal может редактировать только Subject-ы, на которые имеет права. Хранение прав — в PostgreSQL (user_id → subject_code → role).

### 9.4 Кросс-предметный roadmap

При построении roadmap для физики — автоматически включать математические пререквизиты:

```cypher
// Roadmap для физики с математическими зависимостями
MATCH (subj:Subject {subject_code: 'PHYS'})-[:CONTAINS*1..3]->(t:Topic)
WHERE t.tenant_id = $tenant_id
OPTIONAL MATCH (t)-[uk:USES_KNOWLEDGE]->(math_dep:Topic)
RETURN t.uid, t.title, 'PHYS' AS subject,
       collect({
           uid: math_dep.uid,
           title: math_dep.title,
           subject: 'MATH',
           importance: uk.importance
       }) AS math_dependencies
```

### 9.5 Начальный набор кросс-предметных связей

Для Physics → Mathematics:

| Физика (Topic) | Математика (Topic) | importance | aspect |
|---------------|-------------------|------------|--------|
| Кинематика | Производная | 0.9 | computational |
| Динамика | Векторы | 0.8 | conceptual |
| Электростатика | Интеграл | 0.7 | computational |
| Оптика | Тригонометрия | 0.6 | computational |
| Статистическая физика | Вероятность | 0.8 | conceptual |
| Колебания | Тригонометрические функции | 0.9 | computational |

### 9.6 Canonical spec — обновления

```python
ALLOWED_NODE_LABELS = {
    ...,
    "Competency",
}

ALLOWED_EDGE_TYPES = {
    ...,
    "USES_KNOWLEDGE",
    "DEVELOPED_BY",
    "ASSESSED_IN",
    "REQUIRES_COMPETENCY",
}
```

### 9.7 Критерии завершения

- [ ] `Competency` добавлен в `ALLOWED_NODE_LABELS`
- [ ] `USES_KNOWLEDGE`, `DEVELOPED_BY`, `ASSESSED_IN`, `REQUIRES_COMPETENCY` добавлены в `ALLOWED_EDGE_TYPES`
- [ ] Второй Subject (Physics) создан с базовой иерархией (≥5 Section, ≥20 Topic)
- [ ] USES_KNOWLEDGE связи между Physics и Mathematics (≥15 связей)
- [ ] Кросс-предметный roadmap работает
- [ ] Permission model в proposal system разграничивает предметы

---

## 10. P8 — Adaptive Difficulty Micro-Graph

### 10.1 Проблема

Внутри одной темы все Example имеют `difficulty_level` (1–10), но нет **структурированной прогрессии сложности**. Ученик может получить задание уровня 5 сразу после уровня 1. Нет scaffolding — плавного перехода от простого к сложному.

### 10.2 Модель данных

> Важно: P8 добавляет только **статическую структуру сложности** в граф.
> Персональное состояние ученика (текущий tier, попытки, mastery по tier) хранится в PostgreSQL StudyNinja.

#### 10.2.1 Новый тип узла: DifficultyTier

```
(:DifficultyTier {
    uid: String,            // "DT-{topic_uid}-L{level}"
    tenant_id: String,
    topic_uid: String,      // к какой теме относится
    level: Integer,         // 1, 2, 3 (количество уровней зависит от темы)
    title: String,          // "Базовый", "Средний", "Продвинутый"
    description: String,    // "Простые примеры с одной операцией"
    unlock_mastery: Float,  // Mastery предыдущего уровня для разблокировки (0.7)
    target_mastery: Float,  // Целевой mastery этого уровня (0.8)
    lifecycle_status: String
})
```

#### 10.2.2 Новые связи

```
(:Topic)-[:HAS_TIER]->(:DifficultyTier)
// "Тема содержит уровень сложности"

(:DifficultyTier)-[:NEXT_TIER]->(:DifficultyTier)
// "После этого уровня идёт следующий"

(:DifficultyTier)-[:TIER_EXAMPLE]->(:Example)
// "Пример относится к этому уровню сложности"

(:DifficultyTier)-[:TIER_METHOD]->(:Method)
// "Метод используется на этом уровне"
```

#### 10.2.3 Граф для одной темы

```
(:Topic {title: "Квадратные уравнения"})
    │
    ├──[:HAS_TIER]──▶ (:DifficultyTier {level: 1, title: "Базовый"})
    │                      │
    │                      ├──[:TIER_EXAMPLE]──▶ "x² = 9"
    │                      ├──[:TIER_EXAMPLE]──▶ "x² - 4 = 0"
    │                      └──[:TIER_METHOD]──▶ "Извлечение корня"
    │                      │
    │                      └──[:NEXT_TIER]──▶
    │
    ├──[:HAS_TIER]──▶ (:DifficultyTier {level: 2, title: "Стандартный"})
    │                      │
    │                      ├──[:TIER_EXAMPLE]──▶ "x² + 5x + 6 = 0"
    │                      ├──[:TIER_EXAMPLE]──▶ "2x² - 3x - 2 = 0"
    │                      └──[:TIER_METHOD]──▶ "Дискриминант"
    │                      │
    │                      └──[:NEXT_TIER]──▶
    │
    └──[:HAS_TIER]──▶ (:DifficultyTier {level: 3, title: "Продвинутый"})
                           │
                           ├──[:TIER_EXAMPLE]──▶ "x⁴ - 5x² + 4 = 0"
                           ├──[:TIER_EXAMPLE]──▶ "|x² - 3x| = 2"
                           └──[:TIER_METHOD]──▶ "Замена переменной"
```

### 10.3 Scaffolding Engine

```python
class ScaffoldingEngine:
    """
    Использует:
      1) статический DifficultyTier-граф в Neo4j;
      2) персональный tier-state из PostgreSQL.
    """

    async def get_next_example(
        self,
        user_uid: str,
        topic_uid: str,
        tenant_id: str = "default",
    ) -> dict | None:
        # 1. Текущий tier/мастери берём из PostgreSQL (StudyNinja)
        state = await self._state_repo.get_topic_tier_state(user_uid, topic_uid)
        current_tier_uid = state.current_tier_uid

        # 2. Из Neo4j берём кандидатов только для этого tier
        # solved_example_uids также берём из PostgreSQL и передаём как exclude.
        query = """
        MATCH (dt:DifficultyTier {uid: $tier_uid, tenant_id: $tenant_id})-[:TIER_EXAMPLE]->(ex:Example)
        WHERE NOT ex.uid IN $exclude_uids
        RETURN ex {.*, tier_level: dt.level} AS example
        ORDER BY ex.difficulty_level ASC
        LIMIT 1
        """
        records = await self._repo.read(query, {
            "tier_uid": current_tier_uid,
            "tenant_id": tenant_id,
            "exclude_uids": state.solved_example_uids,
        })

        if records:
            return records[0]["example"]

        # 3. Если текущий tier исчерпан, проверяем unlock следующего по PG-state
        next_tier = await self._get_next_tier(current_tier_uid, tenant_id)
        if next_tier:
            if state.current_tier_mastery >= state.current_tier_target_mastery:
                await self._state_repo.promote_tier(user_uid, topic_uid, next_tier["uid"])
                return await self.get_next_example(user_uid, topic_uid, tenant_id)

        return None  # Все уровни пройдены

    async def on_incorrect_answer(
        self,
        user_uid: str,
        topic_uid: str,
        current_tier_uid: str,
        tenant_id: str = "default",
    ) -> dict | None:
        # При ошибке выбираем более простой пример в том же tier.
        query = """
        MATCH (dt:DifficultyTier {uid: $tier_uid, tenant_id: $tenant_id})-[:TIER_EXAMPLE]->(ex:Example)
        WHERE ex.difficulty_level < $max_diff
          AND NOT ex.uid IN $exclude_uids
        RETURN ex {.*} AS example
        ORDER BY ex.difficulty_level ASC
        LIMIT 1
        """
        state = await self._state_repo.get_topic_tier_state(user_uid, topic_uid)
        records = await self._repo.read(query, {
            "tier_uid": current_tier_uid,
            "tenant_id": tenant_id,
            "exclude_uids": state.solved_example_uids,
            "max_diff": 5,  # Ниже среднего для текущего tier
        })

        if records:
            return records[0]["example"]

        # Откат на предыдущий tier
        prev_query = """
        MATCH (prev:DifficultyTier {tenant_id: $tenant_id})-[:NEXT_TIER]->(dt:DifficultyTier {uid: $tier_uid, tenant_id: $tenant_id})
        RETURN prev.uid AS uid
        """
        prev = await self._repo.read(prev_query, {"tier_uid": current_tier_uid, "tenant_id": tenant_id})
        if prev:
            await self._state_repo.demote_tier(user_uid, topic_uid, prev[0]["uid"])
            return await self.get_next_example(user_uid, topic_uid, tenant_id)

        return None
```

### 10.4 Canonical spec — обновления

```python
ALLOWED_NODE_LABELS = {
    ...,
    "DifficultyTier",
}

ALLOWED_EDGE_TYPES = {
    ...,
    "HAS_TIER",
    "NEXT_TIER",
    "TIER_EXAMPLE",
    "TIER_METHOD",
}
```

### 10.5 Миграция существующих данных

```python
"""
Автоматическое создание DifficultyTier для каждой Topic
на основе существующих difficulty_level Example-ов.

Стратегия:
  difficulty_level 1–3 → Tier 1 (Базовый)
  difficulty_level 4–6 → Tier 2 (Стандартный)
  difficulty_level 7–10 → Tier 3 (Продвинутый)
"""
TIER_MAPPING = {
    1: {"range": (1, 3), "title": "Базовый", "unlock_mastery": 0.0, "target_mastery": 0.7},
    2: {"range": (4, 6), "title": "Стандартный", "unlock_mastery": 0.7, "target_mastery": 0.8},
    3: {"range": (7, 10), "title": "Продвинутый", "unlock_mastery": 0.8, "target_mastery": 0.9},
}
```

### 10.6 Критерии завершения

- [ ] `DifficultyTier` добавлен в `ALLOWED_NODE_LABELS`
- [ ] `HAS_TIER`, `NEXT_TIER`, `TIER_EXAMPLE`, `TIER_METHOD` добавлены в `ALLOWED_EDGE_TYPES`
- [ ] DifficultyTier-ы созданы для всех 224 Topic (3 tier на тему = 672 узла)
- [ ] Существующие Example привязаны к tier через TIER_EXAMPLE
- [ ] ScaffoldingEngine интегрирован в lesson flow
- [ ] При неправильном ответе ученик получает более простой пример (а не случайный)
- [ ] Tier-state пользователя хранится в PostgreSQL, без materialized user-графа в Neo4j

---

## 11. P9 — Knowledge Graph Versioning и A/B-тестирование топологий

### 11.1 Проблема

Текущая proposal-система трекает мутации, но нет **снапшотов подграфов**. Невозможно:

1. Откатить конкретный Subsection к предыдущему состоянию
2. Запустить A/B-тест: «Группа A учится с PREREQ-топологией X, группа B — с топологией Y»
3. Сравнить эффективность разных деревьев навыков

### 11.2 Модель данных

#### 11.2.1 Новый тип узла: GraphSnapshot

```
(:GraphSnapshot {
    uid: String,              // "SNAP-{subsection_uid}-{timestamp}"
    tenant_id: String,
    scope_uid: String,        // uid подграфа (Subsection / Section / Subject)
    scope_label: String,      // "Subsection" | "Section" | "Subject"
    version: Integer,         // Версия снапшота (автоинкремент)
    created_at: DateTime,
    created_by: String,       // user_id или "system"
    description: String,      // "Перед реорганизацией пререквизитов алгебры"
    node_count: Integer,      // Количество узлов в снапшоте
    edge_count: Integer,      // Количество связей
    checksum: String          // SHA256 canonical hash всего подграфа
})
```

#### 11.2.2 Хранение снапшотов

Снапшоты хранятся **в PostgreSQL** (не в Neo4j) — это структурированные JSON-дампы:

```sql
CREATE TABLE graph_snapshots (
    id SERIAL PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    tenant_id TEXT NOT NULL DEFAULT 'default',
    scope_uid TEXT NOT NULL,
    scope_label TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by TEXT,
    description TEXT,
    node_count INTEGER,
    edge_count INTEGER,
    checksum TEXT,
    nodes_json JSONB NOT NULL,    -- [{uid, _label, properties...}, ...]
    edges_json JSONB NOT NULL,    -- [{from_uid, to_uid, _type, properties...}, ...]
    UNIQUE(tenant_id, scope_uid, version)
);

CREATE INDEX idx_snapshots_scope ON graph_snapshots(tenant_id, scope_uid);
```

### 11.3 Snapshot API

#### 11.3.1 Создание снапшота

`POST /v1/admin/snapshots`

```json
{
  "scope_uid": "SUBSEC-URAVNENIYA-22d106",
  "description": "Перед реорганизацией PREREQ"
}
```

#### 11.3.2 Восстановление из снапшота

`POST /v1/admin/snapshots/{snapshot_uid}/restore`

Логика:
1. Прочитать snapshot из PostgreSQL
2. Создать proposal с операциями, приводящими текущий подграф к состоянию снапшота
3. Пройти обычный pipeline: validate → commit

#### 11.3.3 Сравнение снапшотов

`GET /v1/admin/snapshots/diff?from={snap_uid_1}&to={snap_uid_2}`

```json
{
  "added_nodes": [...],
  "removed_nodes": [...],
  "modified_nodes": [...],
  "added_edges": [...],
  "removed_edges": [...],
  "modified_edges": [...]
}
```

### 11.4 A/B-тестирование топологий

#### 11.4.1 Концепция

Для A/B-теста создаются **два tenant-а** (или два варианта подграфа), и ученики случайно распределяются между ними:

```
Вариант A (control):
  Topic "Квадратные уравнения"
    PREREQ → "Линейные уравнения" (weight=0.9)
    PREREQ → "Факторизация" (weight=0.7)

Вариант B (treatment):
  Topic "Квадратные уравнения"
    PREREQ → "Линейные уравнения" (weight=0.9)
    PREREQ → "Графики параболы" (weight=0.6)  // Другой путь!
```

#### 11.4.2 Таблица экспериментов в PostgreSQL

```sql
CREATE TABLE ab_experiments (
    id SERIAL PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    tenant_id TEXT NOT NULL DEFAULT 'default',
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',   -- 'draft' | 'running' | 'completed' | 'aborted'
    scope_uid TEXT NOT NULL,       -- uid подграфа, на котором тестируем
    variant_a_snapshot TEXT,       -- snapshot_uid контрольной группы
    variant_b_snapshot TEXT,       -- snapshot_uid экспериментальной группы
    split_ratio FLOAT DEFAULT 0.5,
    metric TEXT NOT NULL,          -- 'mastery_gain' | 'time_to_complete' | 'error_rate'
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    result_json JSONB              -- итоги эксперимента
);

CREATE TABLE ab_assignments (
    user_uid TEXT NOT NULL,
    experiment_uid TEXT NOT NULL,
    variant TEXT NOT NULL,         -- 'A' | 'B'
    assigned_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_uid, experiment_uid)
);
```

#### 11.4.3 Routing запросов

В roadmap planner, если пользователь участвует в A/B-тесте:

```python
async def plan_route_with_ab(
    user_uid: str,
    subject_uid: str,
    progress: dict,
    tenant_id: str,
    **kwargs,
) -> list[dict]:
    """Roadmap с учётом A/B-тестов."""

    # Проверить, есть ли активный эксперимент для пользователя
    assignment = await get_ab_assignment(user_uid)

    if assignment:
        # Использовать подграф варианта (A или B)
        experiment = await get_experiment(assignment["experiment_uid"])
        snapshot_uid = (
            experiment["variant_a_snapshot"]
            if assignment["variant"] == "A"
            else experiment["variant_b_snapshot"]
        )
        # Подменить PREREQ-связи в пределах scope
        override_edges = await get_snapshot_edges(snapshot_uid)
        return await plan_route(
            subject_uid, progress, tenant_id=tenant_id,
            prereq_overrides=override_edges, **kwargs
        )

    return await plan_route(subject_uid, progress, tenant_id=tenant_id, **kwargs)
```

### 11.5 Автоматические снапшоты

Триггер в commit worker — автоматически создавать snapshot при значительных изменениях:

```python
# В commit.py, после успешного коммита:
affected_subsections = get_affected_subsections(operations)
for subsec_uid in affected_subsections:
    # Если изменено >5 узлов или любой PREREQ — auto-snapshot
    if count_changes(operations, subsec_uid) > 5 or has_prereq_changes(operations):
        await create_snapshot(
            scope_uid=subsec_uid,
            description=f"Auto-snapshot before proposal {proposal_id}",
            created_by="system",
        )
```

### 11.6 Критерии завершения

- [ ] PostgreSQL-таблица `graph_snapshots` создана
- [ ] API для создания/восстановления/сравнения снапшотов
- [ ] Auto-snapshot при значительных изменениях через proposal
- [ ] A/B-тестирование: таблицы, assignment, routing
- [ ] Dashboard для сравнения метрик вариантов A vs B

---

## 12. Сводная матрица изменений

### 12.1 Новые типы узлов

| Узел | Приоритет | Зависит от | Примерное количество |
|------|-----------|-----------|---------------------|
| Misconception | P2 | — | ~50–200 |
| LearningObjective | P6 | — | ~500 (224 topics × ~2 levels) |
| DifficultyTier | P8 | — | ~672 (224 topics × 3 tiers) |
| Competency | P7 | — | ~50–100 (ФГОС) |
| GraphSnapshot | P9 | — | В PostgreSQL, не Neo4j |

### 12.2 Новые типы связей

| Связь | Приоритет | Направление | Примерное количество |
|-------|-----------|------------|---------------------|
| COMPOSES | P3 | Skill→Skill | ~300+ |
| COMMON_IN | P2 | Misconception→Topic | ~200 |
| RESOLVED_BY | P2 | Misconception→Method | ~150 |
| INDICATES_GAP_IN | P2 | Misconception→Skill | ~100 |
| CONTRADICTS | P2 | Misconception→Misconception | ~30 |
| HAS_OBJECTIVE | P6 | Topic→LearningObjective | ~500 |
| ASSESSED_BY | P6 | LearningObjective→Example | ~1000 |
| TAUGHT_BY | P6 | LearningObjective→Method | ~500 |
| HAS_TIER | P8 | Topic→DifficultyTier | ~672 |
| NEXT_TIER | P8 | DifficultyTier→DifficultyTier | ~448 |
| TIER_EXAMPLE | P8 | DifficultyTier→Example | ~2654 |
| TIER_METHOD | P8 | DifficultyTier→Method | ~1985 |
| USES_KNOWLEDGE | P7 | Topic→Topic (cross-subject) | ~50+ |
| DEVELOPED_BY | P7 | Competency→Topic | ~200 |
| ASSESSED_IN | P7 | Competency→LearningObjective | ~100 |
| REQUIRES_COMPETENCY | P7 | Competency→Competency | ~30 |

Примечание по P5: learner-state хранится в PostgreSQL-таблицах, поэтому новые user-specific рёбра в Neo4j не добавляются.

### 12.3 Новые свойства на существующих узлах/связях

| Узел/Связь | Свойство | Тип | Приоритет |
|------------|----------|-----|-----------|
| PREREQ | weight | Float [0,1] | P1 |
| PREREQ | is_hard | Boolean | P1 |
| PREREQ | aspect | String enum | P1 |
| PREREQ | description | String | P1 |
| Example | bloom_level | Integer [1-6] | P6 |
| Method | bloom_level | Integer [1-6] | P6 |
| Skill | composition_depth | Integer | P3 |
| Skill | is_atomic | Boolean | P3 |
| * (все узлы) | embedding | Float[] (1536-dim) | P4 |

### 12.4 Обновление canonical.py

Итоговый `ALLOWED_NODE_LABELS`:

```python
ALLOWED_NODE_LABELS = {
    # Существующие
    "Subject", "Section", "Subsection", "Topic", "Skill", "Method",
    "Goal", "Objective", "Example", "Error", "ContentUnit",
    "Concept", "Formula", "TaskType",
    # Новые
    "Misconception",      # P2
    "LearningObjective",  # P6
    "DifficultyTier",     # P8
    "Competency",         # P7
}
```

Итоговый `ALLOWED_EDGE_TYPES`:

```python
ALLOWED_EDGE_TYPES = {
    # Существующие
    "CONTAINS", "PREREQ", "USES_SKILL", "LINKED", "TARGETS",
    "HAS_EXAMPLE", "HAS_UNIT", "MEASURES", "BASED_ON",
    "REQUIRES_SKILL", "HAS_METHOD",
    # Новые
    "COMPOSES",              # P3
    "COMMON_IN",             # P2
    "RESOLVED_BY",           # P2
    "INDICATES_GAP_IN",      # P2
    "CONTRADICTS",           # P2
    "HAS_OBJECTIVE",         # P6
    "ASSESSED_BY",           # P6
    "TAUGHT_BY",             # P6
    "HAS_TIER",              # P8
    "NEXT_TIER",             # P8
    "TIER_EXAMPLE",          # P8
    "TIER_METHOD",           # P8
    "USES_KNOWLEDGE",        # P7
    "DEVELOPED_BY",          # P7
    "ASSESSED_IN",           # P7
    "REQUIRES_COMPETENCY",   # P7
}
```

---

## 13. Порядок миграции

### 13.1 Фазы реализации

```
M0 (неделя 1): Stabilization baseline (P0 + измерения)
  - Исправление orphan-узлов, валидация в commit, CI-валидатор дампов.
  - Базовые метрики: roadmap latency, vector search latency, commit success rate.
  - Выход: «чистый» граф + повторяемые метрики до изменений.

M1 (недели 2–3): Core unlock MVP (P1)
  - Weighted PREREQ с feature flag `weighted_prereq`.
  - Отдельный поток калибровки базовых весов: `prereq_weights_v1.csv` → batch apply → QA coverage report.
  - API совместимость: старый контракт жив, новый readiness — опционально.
  - Выход: управляемая разблокировка тем без регрессии текущего roadmap.

M2 (недели 4–5): Search simplification MVP (P4)
  - Neo4j vector indexes + миграция embeddings.
  - Переход через dual-run: shadow read в Neo4j при основном Qdrant.
  - Cutover только после сравнения качества/latency; fallback на Qdrant до стабилизации.

M3 (недели 6–7): Error intelligence MVP (P2-lite)
  - Misconception detector только pattern + keyword (LLM-этап отложен).
  - Телеметрия детекций и ручная валидация top-N ошибок.
  - Выход: объяснимые подсказки по типичным ошибкам в основных темах.

M4 (недели 8–9): Learner state MVP (P5-lite)
  - PostgreSQL-first learner-state (`user_topic_state`, `user_skill_state`, `user_example_attempts`, `user_misconception_state`).
  - Event-driven запись из `check_answer`, privacy guardrails, без user-state в Neo4j.
  - Выход: базовая персонализация и данные для следующих фаз.

Post-MVP (после недели 9): расширения
  - P3 Skill Composition, P6 Bloom, P8 Difficulty tiers, P9 Snapshots/A-B, P7 Multi-subject.
  - Каждое направление запускается как отдельный RFC-lite с метриками эффекта.
```

### 13.2 MVP-гейты качества (go/no-go)

```
Gate A (после M0):
  - 0 orphan-узлов без label в tenant=default
  - CI-валидатор блокирует merge при нарушениях

Gate B (после M1):
  - p95 `GET /v1/engine/roadmap` не хуже baseline более чем на 10%
  - Доля «ложно заблокированных» тем снижается (контрольная выборка)

Gate C (после M2):
  - p95 vector/hybrid search <= 20ms на текущем масштабе
  - Расхождение top-k между Qdrant и Neo4j в пределах целевого порога

Gate D (после M3):
  - precision@1 для misconception detection на ручной валидации >= 0.70
  - Нет регрессии в check_answer SLA

Gate E (после M4):
  - write path в PostgreSQL learner-state устойчив (ошибки записи < 0.5%)
  - подтверждена корректность cascade delete learner-state при удалении пользователя
```

### 13.3 Совместимость

Все изменения спроектированы как **аддитивные**:
- Новые типы узлов и связей **не ломают** существующие запросы
- Свойства `weight`, `bloom_level` имеют дефолтные значения
- Старый API продолжает работать без изменений
- Новая функциональность доступна через новые endpoint-ы

### 13.4 Rollback-стратегия

Для каждой MVP-фазы:
1. Перед началом — snapshot + метрики baseline (latency, error-rate, conversion).
2. Все изменения canonical spec и planner logic — через feature flags.
3. Cutover делается только после прохождения соответствующего gate.
4. При откате: выключить flag, откатить write-path, вернуть предыдущий индекс/роутинг.
5. Для P4 (vector) поддерживать fallback к Qdrant до завершения M4.

```python
# Feature flags в config
FEATURES = {
    "weighted_prereq": False,      # P1
    "misconceptions": False,       # P2
    "skill_composition": False,    # P3
    "neo4j_vector": False,         # P4
    "learner_state_pg": False,     # P5
    "bloom_taxonomy": False,       # P6
    "multi_subject": False,        # P7
    "difficulty_tiers": False,     # P8
    "graph_snapshots": False,      # P9
}
```

---

## Итого

В версии 1.1 фокус смещён с «сразу всё» на **реалистичный phased MVP за 9 недель** с измеримыми go/no-go гейтами.

После MVP и последующих расширений граф знаний трансформируется из **статического каталога тем** в **живую адаптивную систему**, которая:

1. **Понимает силу связей** (weighted PREREQ) → умные маршруты
2. **Диагностирует ошибки** (Misconception) → мгновенная помощь
3. **Моделирует навыки как дерево** (Skill composition) → RPG-мотивация
4. **Ищет по смыслу внутри графа** (Neo4j vector) → гибридные запросы
5. **Помнит путь ученика** (Learner state) → персонализация + collaborative filtering
6. **Учитывает когнитивную нагрузку** (Bloom) → правильная последовательность
7. **Связывает предметы** (Multi-subject) → целостная картина знаний
8. **Ведёт по сложности** (Difficulty tiers) → scaffolding без frustration
9. **Тестирует гипотезы** (A/B versioning) → data-driven оптимизация топологии

Масштаб графа после всех фаз: ~10–15K узлов, ~20–30K связей (без Learner State). С Learner State — рост пропорционален числу активных учеников × активность.
