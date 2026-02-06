# КnowledgeBase Graph Dataset Export

Экспорт полной структуры графа базы знаний в формате JSONL (JSON Lines).

Дата создания: 2026-02-06
Источники: Neo4j (граф) + PostgreSQL (curricula)

## Структура датасета

### 1. Узлы графа (Graph Nodes)

#### subjects.jsonl (1 запись)
Корневой узел предметной области (Mathematics).
```json
{"uid":"MATH-FULL-V1","title":"Mathematics","description":"","tenant_id":"default","user_class_min":1,"user_class_max":11}
```

#### sections.jsonl (13 записей)
Разделы математики (Арифметика, Алгебра, Геометрия и т.д.).
```json
{"uid":"SEC-ARITHMETIC","title":"Арифметика","description":""}
```

#### subsections.jsonl (25 записей)
Подразделы внутри секций.
```json
{"uid":"SUB-NATURALNYE-CHISLA-1a3f3d","title":"Натуральные числа","description":""}
```

#### topics.jsonl (153 записи)
Темы (учебные единицы).
```json
{"uid":"TOP-NATURALNYE-CHISLA-b27027","title":"Натуральные числа","description":""}
```

#### skills.jsonl (273 записи)
Навыки (конкретные умения).
```json
{"uid":"SKILL-NATURALNYE-CHISLA-OPREDELENIE-cbe29a","title":"Определение натуральных чисел"}
```

#### methods.jsonl (528 записей)
Методы решения (детализация навыков).
```json
{"uid":"METHOD-NATURALNYE-CHISLA-OPREDELENIE-PRIMERY-4cd57e","title":"Примеры натуральных чисел"}
```

**Итого узлов графа: 993**

### 2. Отношения (Graph Relationships)

#### prereq_relationships.jsonl (1082 связи)
Логические зависимости (PREREQ): что требуется изучить перед чем.
```json
{"source_uid":"SKILL-...","target_uid":"METHOD-...","source_label":"Skill","target_label":"Method"}
```

Типы связей:
- Topic → Skill
- Topic → Topic
- Skill → Method
- Skill → Skill

#### contains_relationships.jsonl (191 связь)
Иерархическая структура (CONTAINS): кто включает кого.
```json
{"parent_uid":"SUB-...","child_uid":"TOP-...","parent_label":"Subsection","child_label":"Topic"}
```

Иерархия:
- Subject → Section
- Section → Subsection
- Subsection → Topic

**Итого связей графа: 1273**

### 3. Curricula (PostgreSQL)

#### curricula.jsonl (14 записей)
Учебные программы с разбивкой по целевым оценкам/баллам.

**Базовые curricula (3):** Полные программы всех заданий

**Целевые curricula (11):** Персонализированные программы по оценкам:
- ОГЭ 2026: на 3, на 4, на 5
- ЕГЭ База 2026: на 3, на 4, на 5
- ЕГЭ Профиль 2026: 60+, 70+, 80+, 90+, 95-100 баллов

```json
{"id":12,"code":"RU-OGE-2026-G3","title":"ОГЭ 2026 Математика - На 3","standard":"OGE","language":"ru","status":"active"}
```

#### curriculum_nodes.jsonl (503 записи)
Привязка тем графа к curricula. Целевые curricula содержат только необходимые темы.

```json
{"id":1,"curriculum_id":12,"canonical_uid":"TOP-TEKSTOVYE-ZADACHI-004","kind":"topic","order_index":1,"is_required":true,"exam_task_number":"1-5"}
```

Поля:
- `curriculum_id`: ссылка на curricula.id
- `canonical_uid`: ссылка на узлы графа (Topic)
- `order_index`: порядок изучения в программе
- `exam_task_number`: номера заданий экзамена (согласно ФИПИ 2026)

## Статистика

### Узлы по типам
- Subject: 1
- Section: 13
- Subsection: 25
- Topic: 153
- Skill: 273
- Method: 528
- **Всего**: 993

### Связи по типам
- PREREQ: 1082 (логические зависимости)
- CONTAINS: 191 (иерархическая структура)
- **Всего**: 1273

### Curricula
- Curricula: 14 (3 базовых + 11 целевых программ)
  - ОГЭ: 4 варианта (базовый + на 3, 4, 5)
  - ЕГЭ База: 4 варианта (базовый + на 3, 4, 5)
  - ЕГЭ Профиль: 6 вариантов (базовый + 60+, 70+, 80+, 90+, 100)
- Curriculum Nodes: 503 (привязка тем к программам)

## Свойства графа

- **Тип графа**: DAG (Directed Acyclic Graph)
- **Циклы**: 0 (проверено)
- **Orphaned узлы**: 0 (все узлы связаны)
- **Плотность**: Разреженный (sparsified) - max 10 навыков на тему
- **Семантика**: Все связи релевантны (76.7% нерелевантных навыков удалены)

## Использование

### Чтение узлов
```python
import json

with open('topics.jsonl') as f:
    for line in f:
        topic = json.loads(line)
        print(topic['uid'], topic['title'])
```

### Чтение связей
```python
with open('prereq_relationships.jsonl') as f:
    for line in f:
        rel = json.loads(line)
        print(f"{rel['source_uid']} requires {rel['target_uid']}")
```

### Восстановление графа
Для восстановления полного графа используйте Cypher скрипты:
1. Создайте узлы из subjects → sections → subsections → topics → skills → methods
2. Создайте CONTAINS связи из contains_relationships.jsonl
3. Создайте PREREQ связи из prereq_relationships.jsonl

## Источники данных

- **Neo4j**: bolt://localhost:7687 (граф knowledge base)
- **PostgreSQL**: localhost:5432/knowledgebase (curricula metadata)

## Версия

Экспорт соответствует состоянию после:
- Удаления orphaned узлов (902 skills, 1795 methods)
- Sparsification (1082 PREREQ осталось из 3831)
- Валидации exam_task_number по ФИПИ 2026
- DAG invariant проверки

## Замечания

- Все exam_task_number валидированы по официальным источникам ФИПИ 2026
- Граф разреженный: макс 10 навыков на тему
- Удалены все нерелевантные связи (например, Арифметика → Тригонометрия)
- Тригонометрия удалена из ОГЭ curricula (не входит в экзамен)
