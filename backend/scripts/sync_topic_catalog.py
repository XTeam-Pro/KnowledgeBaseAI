#!/usr/bin/env python3
"""
Скрипт синхронизации темы из графа с каталогом kb_catalog_full.md
- Анализирует методы темы в графе
- Сравнивает с каталогом
- Дополняет недостающие методы
- Обновляет статус до ready2.0
"""

import json
import re
import sys
from pathlib import Path


def load_graph():
    """Загрузка графа из JSONL файлов"""
    entities_path = (
        Path(__file__).parent.parent / "app/services/kb/graph_entities.jsonl"
    )
    rels_path = (
        Path(__file__).parent.parent / "app/services/kb/graph_relationships.jsonl"
    )

    with open(entities_path, "r", encoding="utf-8") as f:
        entities = [json.loads(line) for line in f if line.strip()]

    with open(rels_path, "r", encoding="utf-8") as f:
        rels = [json.loads(line) for line in f if line.strip()]

    return entities, rels


def get_topic_methods(entities, rels, topic_uid):
    """Получение всех методов темы через связи"""
    # Найти связанные skills
    skill_uids = set()
    for r in rels:
        if r.get("type") == "REQUIRES_SKILL" and r.get("from_uid") == topic_uid:
            skill_uids.add(r.get("to_uid"))

    # Найти методы через skills
    method_uids = set()
    for r in rels:
        if r.get("type") == "HAS_METHOD" and r.get("from_uid") in skill_uids:
            method_uids.add(r.get("to_uid"))

    # Получить данные методов
    methods = []
    for m_uid in method_uids:
        method_data = next((e for e in entities if e.get("uid") == m_uid), None)
        if method_data:
            # Получить примеры
            ex_uids = [
                r["to_uid"]
                for r in rels
                if r.get("type") == "HAS_EXAMPLE" and r.get("from_uid") == m_uid
            ]
            examples = [
                next((e for e in entities if e.get("uid") == ex_uid), None)
                for ex_uid in ex_uids
            ]
            methods.append(
                {
                    "uid": m_uid,
                    "data": method_data,
                    "examples": [ex for ex in examples if ex],
                }
            )

    return methods


def get_catalog_section(content, topic_uid):
    """Получение секции темы из каталога"""
    # Ищем по UID темы
    pattern = f"`Topic UID`: `{topic_uid}`"
    start = content.find(pattern)
    if start == -1:
        return "", -1

    # Находим начало секции (строка с #### Topic:)
    section_start = content.rfind("\n#### Topic:", 0, start)
    if section_start == -1:
        section_start = 0
    else:
        section_start += 1

    # Находим конец секции (следующая тема)
    next_topic = content.find("\n#### Topic:", start + 10)
    if next_topic == -1:
        section = content[section_start:]
    else:
        section = content[section_start:next_topic]

    return section, section_start


def get_methods_in_catalog(section):
    """Получение списка методов из секции каталога"""
    if not section:
        return []
    pattern = r"##### Метод: .+\n`UID`: `([A-Z0-9-]+)`"
    return re.findall(pattern, section)


def format_method_entry(method):
    """Форматирование записи метода для каталога"""
    m = method["data"]
    examples = method["examples"]

    title = m.get("title", "Без названия")
    uid = m.get("uid")
    role = m.get("method_role", "practice")
    order = m.get("learning_order", 0)
    grade = m.get("user_class_min", 8)
    class_min = m.get("user_class_min", grade)
    class_max = m.get("user_class_max", grade)
    visualization = m.get("visualization") or "geometric_figure"
    key_formula = m.get("key_formula") or "Нет формулы."
    description = m.get("description", "Описание отсутствует.")
    algorithm_steps = m.get("algorithm_steps", [])

    lines = []
    lines.append(f"##### Метод: {title}")
    lines.append(
        f"`UID`: `{uid}` | `learning_order`: `{order}` | `role`: `{role}` | `grade`: `{grade}` | `class_range`: `{class_min}-{class_max}` | `visualization`: `{visualization}` | `visualization_type`: `-` | `answer_type`: `-`"
    )
    lines.append("")
    lines.append("**Key Formula**")
    lines.append(key_formula)
    lines.append("")
    lines.append("**Описание**")
    lines.append(description)
    lines.append("")
    lines.append("**Шаги алгоритма**")
    for i, step in enumerate(algorithm_steps, 1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("**Примеры**")

    # Формат примеров как в каталоге (первые 3)
    for j, ex in enumerate(examples[:3], 1):
        statement = ex.get("title", "Задача")
        desc = ex.get("description", "")
        answer = "Ответ не указан."
        if "Ответ:" in desc:
            answer = desc.split("Ответ:")[1].strip().split("\n")[0]

        diff = ex.get("difficulty", "средний")
        diff_map = {"легкий": "легкий", "средний": "средний", "сложный": "сложный"}
        difficulty = diff_map.get(str(diff), "средний")

        lines.append(f"{j}. {statement}")
        lines.append(f"Задача: {statement}")
        lines.append(f"Ответ: {answer}")
        lines.append(f"Difficulty: {difficulty}")

    lines.append("")

    return "\n".join(lines)


def update_method_in_catalog(content, method):
    """Обновление существующего метода в каталоге (key_formula и пр.)"""
    m = method["data"]
    uid = m.get("uid")
    key_formula = m.get("key_formula") or "Нет формулы."

    # Найти секцию метода
    pattern = f"`UID`: `{uid}`"
    start = content.find(pattern)
    if start == -1:
        return content, False

    # Найти начало секции метода (строка с ##### Метод:)
    method_start = content.rfind("\n##### Метод:", 0, start)
    if method_start == -1:
        method_start = content.rfind("\n#### Topic:", 0, start)
        if method_start == -1:
            return content, False
    method_start += 1

    # Найти конец секции метода (следующий ##### Метод: или ---)
    next_method = content.find("\n##### Метод:", start + 10)
    next_sep = content.find("\n---", start + 10)
    if next_method == -1 and next_sep == -1:
        method_end = len(content)
    elif next_method == -1:
        method_end = next_sep
    elif next_sep == -1:
        method_end = next_method
    else:
        method_end = min(next_method, next_sep)

    # Проверить есть ли уже Key Formula
    section = content[method_start:method_end]
    if "**Key Formula**" in section:
        # Заменить значение после **
        key_pattern = r"(\*\*Key Formula\*\*\n)[^\n]+(\n)"

        def replacer(m):
            return m.group(1) + key_formula + m.group(2)

        new_section = re.sub(key_pattern, replacer, section, count=1)
        content = content[:method_start] + new_section + content[method_end:]
        return content, True

    return content, False


def sync_topic_catalog(topic_uid):
    """Основная функция синхронизации темы"""
    print(f"Синхронизация темы: {topic_uid}")

    # Загрузка графа
    entities, rels = load_graph()

    # Получение методов из графа
    graph_methods = get_topic_methods(entities, rels, topic_uid)
    graph_method_uids = {m["uid"] for m in graph_methods}
    print(f"Методов в графе: {len(graph_method_uids)}")

    # Загрузка каталога
    catalog_path = Path(__file__).parent.parent / "app/services/kb/kb_catalog_full.md"
    with open(catalog_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Получение секции темы
    section, section_start = get_catalog_section(content, topic_uid)
    if section_start == -1:
        print(f"ERROR: Тема {topic_uid} не найдена в каталоге")
        return False

    # Получение методов из каталога
    catalog_method_uids = set(get_methods_in_catalog(section))
    print(f"Методов в каталоге: {len(catalog_method_uids)}")

    # Найти недостающие методы
    missing_uids = graph_method_uids - catalog_method_uids
    print(f"Методов для добавления: {len(missing_uids)}")

    if missing_uids:
        # Добавить недостающие методы
        new_methods_content = []
        for m in graph_methods:
            if m["uid"] in missing_uids:
                new_methods_content.append(format_method_entry(m))

        # Найти позицию для вставки (перед --- в конце секции)
        sep_pos = section.rfind("\n---")
        if sep_pos == -1:
            sep_pos = len(section)

        # Вставить новые методы
        insert_pos = section_start + sep_pos + 1
        content = (
            content[:insert_pos]
            + "\n"
            + "\n".join(new_methods_content)
            + content[insert_pos:]
        )

        print(f"Добавлено методов: {len(missing_uids)}")

    # Обновить существующие методы (key_formula и пр.)
    updated_count = 0
    for m in graph_methods:
        if m["uid"] in catalog_method_uids:
            content, updated = update_method_in_catalog(content, m)
            if updated:
                updated_count += 1

    print(f"Обновлено методов: {updated_count}")

    # Обновить заголовок темы (счётчик методов и статус)
    # Найти строку с Topic UID
    topic_line_pattern = f"`Topic UID`: `{topic_uid}`.*?\n"
    match = re.search(topic_line_pattern, content)
    ready2_updated = False
    if match:
        old_line = match.group(0).rstrip("\n")
        # Обновить счётчик и статус
        new_line = old_line
        new_line = re.sub(
            r"`Methods`: `\d+`", f"`Methods`: `{len(graph_method_uids)}`", new_line
        )
        new_line = re.sub(r"`Tag`: `\w+`", "`Tag`: `ready2.0`", new_line)

        # Проверить, был ли уже ready2.0
        old_tag_match = re.search(r"`Tag`: `(\w+)`", old_line)
        old_tag = old_tag_match.group(1) if old_tag_match else ""

        content = content.replace(old_line, new_line)
        print(f"Обновлён заголовок темы: {len(graph_method_uids)} методов, ready2.0")

        # Если тег был не ready2.0 - увеличить счетчик ready2.0
        if old_tag != "ready2.0":
            ready2_updated = True
    else:
        print("WARNING: Не найден заголовок темы для обновления")

    # Обновить счётчик ready2.0 в справочной информации
    if ready2_updated:
        ready2_pattern = r"- 🚀 ready2\.0: `(\d+)`"
        ready2_match = re.search(ready2_pattern, content)
        if ready2_match:
            current_count = int(ready2_match.group(1))
            new_count = current_count + 1
            old_line = ready2_match.group(0)
            new_line = old_line.replace(f"`{current_count}`", f"`{new_count}`")
            content = content.replace(old_line, new_line)
            print(f"Обновлён счётчик ready2.0: {current_count} -> {new_count}")
        else:
            print("WARNING: Не найден счётчик ready2.0 в справочной информации")

    # Сохранить каталог
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Готово!")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python sync_topic_catalog.py <TOPIC_UID>")
        print("Пример: python sync_topic_catalog.py TOP-PLOSHCHAD-TREUGOLNIKA-20260328")
        sys.exit(1)

    topic_uid = sys.argv[1]
    success = sync_topic_catalog(topic_uid)
    sys.exit(0 if success else 1)
