#!/usr/bin/env python3
"""
Скрипт точечной вставки методов и примеров из answer.json в граф
- Удаляет старые примеры по теме (точечно)
- Добавляет новые методы и примеры (точечно)
- Создает связи: skill -> метод -> пример
- Сохраняет порядок и форматирование существующих строк
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ENTITIES_FILE = Path(__file__).parent.parent / "app/services/kb/graph_entities.jsonl"
RELS_FILE = Path(__file__).parent.parent / "app/services/kb/graph_relationships.jsonl"
ANSWER_FILE = Path(__file__).parent.parent / "app/services/kb/answer.json"


def find_topic_skill(rels_data, topic_uid):
    """Находит UID скилла для темы"""
    for r in rels_data:
        if r.get("type") == "REQUIRES_SKILL" and r.get("from_uid") == topic_uid:
            return r.get("to_uid")
    return None


def find_method_uids_by_topic(rels_data, topic_uid):
    """Находит UID всех методов темы через skill"""
    skill_uid = None
    for r in rels_data:
        if r.get("type") == "REQUIRES_SKILL" and r.get("from_uid") == topic_uid:
            skill_uid = r.get("to_uid")
            break

    if not skill_uid:
        return [], None

    method_uids = []
    for r in rels_data:
        if r.get("type") == "HAS_METHOD" and r.get("from_uid") == skill_uid:
            method_uids.append(r.get("to_uid"))
    return method_uids, skill_uid


def find_example_uids_by_methods(rels_data, method_uids):
    """Находит UID всех примеров для списка методов"""
    ex_uids = []
    for m_uid in method_uids:
        for r in rels_data:
            if r.get("type") == "HAS_EXAMPLE" and r.get("from_uid") == m_uid:
                ex_uids.append(r.get("to_uid"))
    return ex_uids


def create_method_entity(method_uid, role, examples_data, learning_order):
    """Создание сущности Method из данных answer.json"""
    ex = examples_data[0]

    return {
        "tenant_id": "default",
        "uid": method_uid,
        "type": "Method",
        "_label": "Method",
        "title": ex.get("title", "Метод"),
        "description": "Метод для темы площадей и поверхностей многогранников",
        "method_role": role,
        "learning_order": learning_order,
        "user_class_min": 10,
        "user_class_max": 11,
        "lifecycle_status": "ACTIVE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "algorithm_steps": [
            "Прочитать условие задачи.",
            "Определить тип многогранника.",
            "Применить соответствующую формулу.",
            "Вычислить результат.",
            "Записать ответ.",
        ],
        "key_formula": "Sполн = Sбок + 2Sосн",
        "answer_type": ex.get("answer_type", "numeric"),
        "visualization_type": "geometric_figure",
    }


def create_example_entity(ex_data):
    """Создание сущности Example из данных answer.json"""
    return {
        "tenant_id": "default",
        "uid": ex_data.get("uid"),
        "type": "Example",
        "_label": "Example",
        "title": ex_data.get("title", "Задача"),
        "statement": ex_data.get("statement", ""),
        "solution": ex_data.get("solution", ""),
        "difficulty": ex_data.get("difficulty", 1),
        "answer_type": ex_data.get("answer_type", "numeric"),
        "solution_steps": ex_data.get("solution_steps", []),
        "hints": ex_data.get("hints", []),
        "viz_params": ex_data.get("viz_params", {}),
        "lifecycle_status": "ACTIVE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "user_class_min": 10,
        "user_class_max": 11,
    }


def create_has_method_rel(skill_uid, method_uid):
    """Создание связи HAS_METHOD"""
    return {
        "tenant_id": "default",
        "uid": f"E-{uuid.uuid4().hex[:12]}",
        "from_uid": skill_uid,
        "to_uid": method_uid,
        "type": "HAS_METHOD",
        "_from_uid": skill_uid,
        "_to_uid": method_uid,
        "_type": "HAS_METHOD",
        "weight": 1.0,
        "confidence": 0.95,
        "kind": "curriculum",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def create_has_example_rel(method_uid, example_uid):
    """Создание связи HAS_EXAMPLE"""
    return {
        "tenant_id": "default",
        "uid": f"E-{uuid.uuid4().hex[:12]}",
        "from_uid": method_uid,
        "to_uid": example_uid,
        "type": "HAS_EXAMPLE",
        "_from_uid": method_uid,
        "_to_uid": example_uid,
        "_type": "HAS_EXAMPLE",
        "weight": 1.0,
        "relevance": 1.0,
        "kind": "curriculum",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def insert_topic_from_answer():
    """Основная функция"""
    print("Загрузка answer.json...")
    with open(ANSWER_FILE, "r", encoding="utf-8") as f:
        answer_data = json.load(f)

    topic_uid = answer_data.get("topic_uid")
    method_updates = answer_data.get("method_updates", [])

    print(f"Topic: {topic_uid}")
    print(f"Методов для обработки: {len(method_updates)}")

    # Загрузка rels (нужно для поиска связей)
    print("\nАнализ связей...")
    rels_data = []
    with open(RELS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rels_data.append(json.loads(line))

    # Найти методы и скилл темы
    current_method_uids, skill_uid = find_method_uids_by_topic(rels_data, topic_uid)
    if not skill_uid:
        print(f"ERROR: Не найден скилл для темы {topic_uid}")
        return False

    print(f"Skill UID: {skill_uid}")
    print(f"Текущих методов: {len(current_method_uids)}")

    # Найти примеры для удаления
    old_example_uids = find_example_uids_by_methods(rels_data, current_method_uids)
    print(f"Примеров для удаления: {len(old_example_uids)}")

    # Определить какие методы нужно удалить (все кроме новых из answer)
    new_method_uids = {m.get("uid") for m in method_updates}
    methods_to_delete = set(current_method_uids) - new_method_uids
    print(f"Методов для удаления: {len(methods_to_delete)}")

    # Создать новые данные для вставки
    new_entities = []
    new_rels = []

    for method_update in method_updates:
        method_uid = method_update.get("uid")
        examples_data = method_update.get("examples", {}).get("create", [])

        if not examples_data:
            continue

        # Определить role и order
        if "INTRO" in method_uid:
            role = "intro"
            learning_order = 0
        elif "PRACTICE" in method_uid:
            role = "practice"
            learning_order = 10
        elif "EXAM" in method_uid:
            role = "exam"
            learning_order = 20
        else:
            role = "core"
            learning_order = 5

        # Создать метод
        method_entity = create_method_entity(
            method_uid, role, examples_data, learning_order
        )
        new_entities.append(json.dumps(method_entity, ensure_ascii=False))

        # Создать связь HAS_METHOD
        has_method_rel = create_has_method_rel(skill_uid, method_uid)
        new_rels.append(json.dumps(has_method_rel, ensure_ascii=False))

        # Создать примеры
        for ex_data in examples_data:
            ex_entity = create_example_entity(ex_data)
            new_entities.append(json.dumps(ex_entity, ensure_ascii=False))

            # Создать связь HAS_EXAMPLE
            has_example_rel = create_has_example_rel(method_uid, ex_data.get("uid"))
            new_rels.append(json.dumps(has_example_rel, ensure_ascii=False))

    print(f"\nНовых сущностей: {len(new_entities)}")
    print(f"Новых связей: {len(new_rels)}")

    # Точечная обработка entities.jsonl
    print("\nОбработка graph_entities.jsonl...")
    lines_removed = 0
    lines_added = 0

    with open(ENTITIES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if not line.strip():
            new_lines.append(line)
            continue

        try:
            obj = json.loads(line)
            uid = obj.get("uid")

            # Удаляем старые примеры
            if uid in old_example_uids:
                lines_removed += 1
                continue

            # Удаляем старые методы темы
            if uid in methods_to_delete:
                lines_removed += 1
                continue

        except json.JSONDecodeError:
            pass

        new_lines.append(line)

    # Добавить новые сущности в конец (после всех существующих)
    for new_ent in new_entities:
        new_lines.append(new_ent + "\n")
        lines_added += 1

    with open(ENTITIES_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"  Удалено строк: {lines_removed}")
    print(f"  Добавлено строк: {lines_added}")

    # Точечная обработка relationships.jsonl
    print("\nОбработка graph_relationships.jsonl...")
    rel_lines_removed = 0
    rel_lines_added = 0

    with open(RELS_FILE, "r", encoding="utf-8") as f:
        rel_lines = f.readlines()

    new_rel_lines = []
    for line in rel_lines:
        if not line.strip():
            new_rel_lines.append(line)
            continue

        try:
            obj = json.loads(line)
            r_type = obj.get("type")
            from_uid = obj.get("from_uid")
            to_uid = obj.get("to_uid")

            # Удаляем старые HAS_EXAMPLE для старых методов
            if r_type == "HAS_EXAMPLE" and from_uid in methods_to_delete:
                rel_lines_removed += 1
                continue

            # Удаляем старые HAS_METHOD для старых методов
            if (
                r_type == "HAS_METHOD"
                and from_uid == skill_uid
                and to_uid in methods_to_delete
            ):
                rel_lines_removed += 1
                continue

        except json.JSONDecodeError:
            pass

        new_rel_lines.append(line)

    # Добавить новые связи в конец
    for new_r in new_rels:
        new_rel_lines.append(new_r + "\n")
        rel_lines_added += 1

    with open(RELS_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_rel_lines)

    print(f"  Удалено строк: {rel_lines_removed}")
    print(f"  Добавлено строк: {rel_lines_added}")

    print("\nГотово!")
    return True


if __name__ == "__main__":
    insert_topic_from_answer()
