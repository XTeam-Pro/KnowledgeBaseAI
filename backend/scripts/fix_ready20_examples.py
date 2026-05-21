#!/usr/bin/env python3
"""Normalize KB methods/examples to the ready2.0 GRR example contract.

The lesson-stage service expects method examples to form this matrix:
  - difficulty=0: worked I_DO example
  - difficulty=1,2,3 without "Самостоятельно:" prefix: WE_DO
  - difficulty=1,2,3 with "Самостоятельно:" prefix: YOU_DO

Older graph snapshots stored a whole "Задача: ... Решение: ..." blob in
Example.description.  That makes the lesson UI show the answer in the stem and
can make the whole solution become correctAnswer.  This script splits those
legacy blobs into statement/solution/answer and fills missing GRR slots.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ENTITIES_PATH = ROOT / "app/services/kb/graph_entities.jsonl"
RELATIONSHIPS_PATH = ROOT / "app/services/kb/graph_relationships.jsonl"
NOW = datetime.now(timezone.utc).isoformat()
TENANT_ID = "default"


PREDSTAVIT_MATRIX: dict[str, dict[str, Any]] = {
    "EX-MET-7-PREDSTAVIT-KAK-DROB-READY20-I": {
        "title": "Представление целого числа в виде дроби",
        "statement": "Представьте число 2 в виде дроби.",
        "solution": "Число 2 — целое. Любое целое число можно записать как дробь со знаменателем 1. Ответ: 2/1.",
        "answer": "2/1",
        "difficulty": 0,
        "solution_steps": [
            "Определяем, что число 2 является целым.",
            "Записываем целое число как дробь со знаменателем 1.",
            "Получаем 2/1.",
        ],
    },
    "EX-MET-7-PREDSTAVIT-KAK-DROB-AUTO-20260326-1": {
        "title": "Представление положительного целого числа в виде дроби",
        "statement": "Представьте число 5 в виде дроби.",
        "solution": "Число 5 — целое. Любое целое число записывается как дробь со знаменателем 1. Ответ: 5/1.",
        "answer": "5/1",
        "difficulty": 1,
        "solution_steps": [
            "Проверяем, что 5 — целое число.",
            "Ставим знаменатель 1.",
            "Получаем 5/1.",
        ],
    },
    "EX-MET-7-PREDSTAVIT-KAK-DROB-AUTO-20260326-2": {
        "title": "Представление отрицательного целого числа в виде дроби",
        "statement": "Представьте число -3 в виде дроби.",
        "solution": "Число -3 — целое. Записываем его в виде дроби со знаменателем 1. Ответ: -3/1.",
        "answer": "-3/1",
        "difficulty": 2,
        "solution_steps": [
            "Проверяем, что -3 — целое число.",
            "Сохраняем знак минус в числителе.",
            "Записываем знаменатель 1 и получаем -3/1.",
        ],
    },
    "EX-MET-7-PREDSTAVIT-KAK-DROB-READY20-WE-3": {
        "title": "Представление нуля в виде дроби",
        "statement": "Представьте число 0 в виде дроби.",
        "solution": "Число 0 — целое. Его можно записать как дробь со знаменателем 1. Ответ: 0/1.",
        "answer": "0/1",
        "difficulty": 3,
        "solution_steps": [
            "Проверяем, что 0 — целое число.",
            "Записываем его со знаменателем 1.",
            "Получаем 0/1.",
        ],
    },
    "EX-MET-7-PREDSTAVIT-KAK-DROB-READY20-YOU-1": {
        "title": "Самостоятельное представление числа 8 в виде дроби",
        "statement": "Самостоятельно: представьте число 8 в виде дроби.",
        "solution": "Число 8 — целое, поэтому знаменатель можно взять равным 1. Ответ: 8/1.",
        "answer": "8/1",
        "difficulty": 1,
        "solution_steps": [
            "Определяем, что 8 — целое число.",
            "Записываем знаменатель 1.",
            "Получаем 8/1.",
        ],
    },
    "EX-MET-7-PREDSTAVIT-KAK-DROB-READY20-YOU-2": {
        "title": "Самостоятельное представление числа -6 в виде дроби",
        "statement": "Самостоятельно: представьте число -6 в виде дроби.",
        "solution": "Число -6 — целое. Знак минус остаётся в числителе, знаменатель равен 1. Ответ: -6/1.",
        "answer": "-6/1",
        "difficulty": 2,
        "solution_steps": [
            "Определяем, что -6 — целое число.",
            "Сохраняем минус в числителе.",
            "Получаем -6/1.",
        ],
    },
    "EX-MET-7-PREDSTAVIT-KAK-DROB-READY20-YOU-3": {
        "title": "Самостоятельное представление числа 11 в виде дроби",
        "statement": "Самостоятельно: представьте число 11 в виде дроби.",
        "solution": "Число 11 — целое. Любое целое число можно записать как дробь со знаменателем 1. Ответ: 11/1.",
        "answer": "11/1",
        "difficulty": 3,
        "solution_steps": [
            "Определяем, что 11 — целое число.",
            "Берём знаменатель 1.",
            "Получаем 11/1.",
        ],
    },
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, separators=(",", ": ")) + "\n")


def strip_task_prefix(text: str) -> str:
    s = text.strip()
    s = re.sub(r"^(самостоятельно:\s*)?задача:\s*", lambda m: (m.group(1) or ""), s, flags=re.IGNORECASE)
    return s.strip()


def derive_statement(blob: str, fallback_title: str = "") -> str:
    raw = str(blob or "").strip()
    if not raw:
        return str(fallback_title or "").strip()
    stem = re.split(r"\bрешение\s*:", raw, maxsplit=1, flags=re.IGNORECASE)[0]
    stem = re.split(r"\n\s*шаг\s*\d+\s*:", stem, maxsplit=1, flags=re.IGNORECASE)[0]
    stem = re.split(r"\bшаг\s*1\s*:", stem, maxsplit=1, flags=re.IGNORECASE)[0]
    stem = re.split(r"\bответ\s*:", stem, maxsplit=1, flags=re.IGNORECASE)[0]
    stem = strip_task_prefix(stem)
    return stem.rstrip().rstrip(".") + "." if stem else str(fallback_title or "").strip()


def derive_solution(row: dict[str, Any]) -> str:
    solution = str(row.get("solution") or "").strip()
    description = str(row.get("description") or "").strip()
    if solution and solution != description:
        return solution
    if "решение:" in description.lower():
        return re.split(r"\bрешение\s*:", description, maxsplit=1, flags=re.IGNORECASE)[1].strip()
    if solution:
        return solution
    return description


def normalize_answer(answer: str) -> str:
    s = re.sub(r"\$+", "", str(answer or "")).strip()
    s = s.rstrip(".;").strip()
    return s


def is_boolean_like_answer(answer: str) -> bool | None:
    s = normalize_answer(answer).lower().replace("ё", "е")
    if not s:
        return None
    if re.fullmatch(r"(1|true|истина|верно|да)", s):
        return True
    if re.fullmatch(r"(0|false|ложь|неверно|нет)", s):
        return False
    if s.startswith(("да,", "да ", "верно", "является")):
        return True
    if s.startswith(("нет,", "нет ", "неверно", "не является")):
        return False
    if any(marker in s for marker in ("доказано", "корректно", "верно", "принадлежит", "подобны", "прямоугольный")):
        if not any(marker in s for marker in ("неверно", "не является", "не принадлежит", "не подобны")):
            return True
    return None


def solution_count_answer(answer: str) -> str | None:
    s = normalize_answer(answer).lower().replace("ё", "е")
    if re.search(r"\b(решений\s+нет|нет\s+решений|не\s+имеет\s+решений)\b", s):
        return "0"
    if re.search(r"\b(одно|единственное|один)\s+решени", s):
        return "1"
    return None


def looks_like_symbolic_answer(answer: str) -> bool:
    value = normalize_answer(answer)
    if not value:
        return False
    if re.fullmatch(r"[-+]?\d+(?:[,.]\d+)?", value):
        return False
    return bool(
        any(mark in value for mark in ("=", "<", ">", "/", "^", "√", "π", "∅", "empty_set", "(", ")", ";", ","))
        or re.search(r"\b[xyabc]\b", value, flags=re.IGNORECASE)
    )


def normalize_logic_example(row: dict[str, Any], answer_bool: bool, assertion: str | None = None) -> None:
    statement = derive_statement(str(row.get("statement") or row.get("description") or row.get("title") or ""))
    if assertion:
        assertion = assertion.strip().rstrip(".")
        statement = f"Верно ли утверждение: {assertion}?"
    elif not re.search(r"\b(ли|верно ли|является ли|может ли|имеет ли|существует ли)\b", statement, flags=re.IGNORECASE):
        statement = f"Верно ли утверждение для задания «{statement.rstrip('.')}»: {normalize_answer(row.get('answer') or '')}?"
    row["statement"] = statement
    row["answer"] = "1" if answer_bool else "0"
    row["answer_type"] = "logic"
    solution = str(row.get("solution") or "").strip()
    if not solution:
        solution = "Да." if answer_bool else "Нет."
    row["solution"] = ensure_answer_line(solution, row["answer"])


def is_modeling_statement(statement: str) -> bool:
    s = str(statement or "").lower()
    return bool(
        re.search(r"\bсостав", s)
        and ("уравнен" in s or "неравенств" in s)
    )


def replace_answer_line(solution: str, answer: str) -> str:
    answer = normalize_answer(answer)
    if not answer:
        return str(solution or "").strip()
    return re.sub(
        r"(\bответ\s*:\s*)[^\n]+",
        lambda match: f"{match.group(1)}{answer}.",
        str(solution or "").strip(),
        flags=re.IGNORECASE,
    )


def extract_answer(solution: str, statement: str = "") -> str:
    s = str(solution or "").strip()
    if not s:
        return ""

    if is_modeling_statement(statement):
        before_answer = re.split(r"\bответ\s*:", s, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        first_sentence = re.split(r"[.;]\s+", before_answer, maxsplit=1)[0].strip()
        if first_sentence:
            return normalize_answer(first_sentence)

    answer_matches = re.findall(r"\bответ\s*:\s*([^\n]+)", s, flags=re.IGNORECASE)
    if answer_matches:
        return normalize_answer(answer_matches[-1])

    got_matches = re.findall(r"\bполучаем\s+([^.;\n]+)", s, flags=re.IGNORECASE)
    if got_matches:
        return normalize_answer(got_matches[-1])

    means_matches = re.findall(r"\bзначит,?\s+([^.;\n]+)", s, flags=re.IGNORECASE)
    if means_matches:
        return normalize_answer(means_matches[-1])

    eq_matches = re.findall(r"=\s*([^=.;\n]+)", s)
    if eq_matches:
        return normalize_answer(eq_matches[-1])

    short = normalize_answer(s)
    if len(short) <= 80:
        return short

    sentences = [part.strip() for part in re.split(r"[.!?]\s+", s) if part.strip()]
    return normalize_answer(sentences[-1]) if sentences else ""


def infer_answer_type(answer: str, statement: str = "") -> str:
    value = normalize_answer(answer)
    if not value:
        return "logic"
    if re.fullmatch(r"[-+]?\d+(?:[,.]\d+)?", value):
        return "numeric"
    if solution_count_answer(value) is not None:
        return "numeric"
    if is_boolean_like_answer(value) is not None:
        return "logic"
    if looks_like_symbolic_answer(value):
        return "symbolic_expression"
    return "logic"


def ensure_answer_line(solution: str, answer: str) -> str:
    base = str(solution or "").strip()
    answer = normalize_answer(answer)
    if not base:
        return f"Ответ: {answer}." if answer else ""
    if re.search(r"\bответ\s*:", base, flags=re.IGNORECASE):
        return replace_answer_line(base, answer) if answer else base
    if not answer:
        return base
    return base.rstrip().rstrip(".") + f". Ответ: {answer}."


def derive_steps(solution: str, answer: str) -> list[str]:
    sentences = [part.strip() for part in re.split(r"[.!?]\s+", str(solution or "")) if part.strip()]
    steps = [s for s in sentences if not s.lower().startswith("ответ:")][:4]
    if answer and not any("ответ" in s.lower() for s in steps):
        steps.append(f"Записываем ответ: {answer}.")
    return steps or (["Записываем решение.", f"Ответ: {answer}."] if answer else ["Записываем решение."])


def make_hints(statement: str, answer_type: str) -> list[str]:
    if answer_type == "text":
        return ["Выделите ключевое требование задачи.", "Сформулируйте ответ коротко и по смыслу."]
    return ["Выделите, что именно нужно найти.", "Выполните преобразование и проверьте итоговый ответ."]


def normalize_example(row: dict[str, Any]) -> bool:
    if row.get("type") != "Example" and row.get("_label") != "Example":
        return False

    changed = False
    title = str(row.get("title") or "").strip()
    statement = str(row.get("statement") or "").strip()
    description = str(row.get("description") or "").strip()

    leaky_statement = bool(
        re.search(r"\bрешение\s*:", statement, flags=re.IGNORECASE)
        or re.search(r"\bответ\s*:", statement, flags=re.IGNORECASE)
        or re.search(r"\bшаг\s*\d+\s*:", statement, flags=re.IGNORECASE)
    )
    if not statement or leaky_statement:
        new_statement = derive_statement(statement or description, title)
        if new_statement and new_statement != statement:
            row["statement"] = new_statement
            changed = True
    else:
        clean = strip_task_prefix(statement)
        if clean != statement:
            row["statement"] = clean
            changed = True

    solution = derive_solution(row)
    statement_for_answer = row.get("statement") or ""
    explicit_answer = normalize_answer(row.get("answer") or row.get("correct_answer") or "")
    answer = (
        extract_answer(solution, statement_for_answer)
        if is_modeling_statement(statement_for_answer)
        else explicit_answer or extract_answer(solution, statement_for_answer)
    )
    solution = ensure_answer_line(solution, answer)

    if solution and row.get("solution") != solution:
        row["solution"] = solution
        changed = True
    if answer and row.get("answer") != answer:
        row["answer"] = answer
        changed = True

    answer_type = str(row.get("answer_type") or "").strip() or infer_answer_type(answer, row.get("statement") or "")
    if answer_type == "text":
        count_answer = solution_count_answer(answer)
        bool_answer = is_boolean_like_answer(answer)
        if count_answer is not None:
            row["answer"] = count_answer
            answer = count_answer
            row["solution"] = ensure_answer_line(solution, answer)
            answer_type = "numeric"
        elif looks_like_symbolic_answer(answer):
            answer_type = "symbolic_expression"
        else:
            normalize_logic_example(row, True if bool_answer is None else bool_answer)
            answer = str(row["answer"])
            solution = str(row["solution"])
            answer_type = "logic"
    if row.get("answer_type") != answer_type:
        row["answer_type"] = answer_type
        changed = True

    if row.get("difficulty") is None:
        diff = row.get("difficulty_level")
        row["difficulty"] = int(diff) if isinstance(diff, int) and 0 <= diff <= 3 else 1
        changed = True

    if not isinstance(row.get("solution_steps"), list) or not row.get("solution_steps"):
        row["solution_steps"] = derive_steps(solution, answer)
        changed = True

    if row.get("difficulty") != 0 and not isinstance(row.get("hints"), list):
        row["hints"] = make_hints(row.get("statement") or "", answer_type)
        changed = True

    if changed:
        row["updated_at"] = NOW
    return changed


def rel_uid(from_uid: str, to_uid: str) -> str:
    digest = hashlib.sha1(f"{from_uid}->{to_uid}:HAS_EXAMPLE".encode("utf-8")).hexdigest()[:16]
    return f"E-{digest}"


def slot_for_example(example: dict[str, Any]) -> tuple[str, int] | None:
    try:
        difficulty = int(example.get("difficulty") if example.get("difficulty") is not None else example.get("difficulty_level"))
    except (TypeError, ValueError):
        return None
    if difficulty == 0:
        return ("i", 0)
    if difficulty in (1, 2, 3):
        statement = str(example.get("statement") or "")
        return ("you" if statement.lower().startswith("самостоятельно:") else "we", difficulty)
    return None


def clone_for_slot(method: dict[str, Any], source: dict[str, Any] | None, stage: str, difficulty: int) -> dict[str, Any]:
    method_uid = str(method["uid"])
    suffix = "I" if stage == "i" else f"{stage.upper()}-{difficulty}"
    uid = f"EX-{method_uid}-READY20-{suffix}"
    title = str(method.get("title") or "Метод").strip()
    base_statement = str((source or {}).get("statement") or f"Выполните задание по методу «{title}».").strip()
    base_statement = re.sub(r"^самостоятельно:\s*", "", base_statement, flags=re.IGNORECASE).strip()
    statement = base_statement
    if stage == "you":
        statement = "Самостоятельно: " + statement[:1].lower() + statement[1:]

    answer = normalize_answer((source or {}).get("answer") or "")
    solution = str((source or {}).get("solution") or "").strip()
    answer_type = str((source or {}).get("answer_type") or method.get("answer_type") or "").strip() or infer_answer_type(answer, statement)
    if not solution:
        solution = f"Применяем метод «{title}». Ответ: {answer}." if answer else f"Применяем метод «{title}»."
    solution = ensure_answer_line(solution, answer)

    return {
        "tenant_id": TENANT_ID,
        "uid": uid,
        "created_at": NOW,
        "updated_at": NOW,
        "lifecycle_status": "ACTIVE",
        "type": "Example",
        "_label": "Example",
        "title": f"{title}: {'разбор' if stage == 'i' else 'тренировка'} {difficulty if stage != 'i' else ''}".strip(),
        "statement": statement,
        "solution": solution,
        "answer": answer,
        "difficulty": difficulty,
        "answer_type": answer_type,
        "solution_steps": derive_steps(solution, answer),
        "hints": [] if stage == "you" else make_hints(statement, answer_type),
        "user_class_min": method.get("user_class_min"),
        "user_class_max": method.get("user_class_max"),
    }


def upsert_example(
    rows: list[dict[str, Any]],
    entities_by_uid: dict[str, dict[str, Any]],
    example: dict[str, Any],
) -> dict[str, Any]:
    uid = str(example["uid"])
    if uid in entities_by_uid:
        target = entities_by_uid[uid]
        target.update(example)
        target["updated_at"] = NOW
        return target
    rows.append(example)
    entities_by_uid[uid] = example
    return example


def ensure_relationship(
    rels: list[dict[str, Any]],
    existing: set[tuple[str, str, str]],
    method_uid: str,
    example_uid: str,
) -> bool:
    key = (method_uid, example_uid, "HAS_EXAMPLE")
    if key in existing:
        return False
    rels.append(
        {
            "tenant_id": TENANT_ID,
            "uid": rel_uid(method_uid, example_uid),
            "from_uid": method_uid,
            "to_uid": example_uid,
            "type": "HAS_EXAMPLE",
            "_from_uid": method_uid,
            "_to_uid": example_uid,
            "_type": "HAS_EXAMPLE",
            "updated_at": NOW,
            "weight": 1.0,
            "relevance": 1.0,
            "kind": "curriculum",
        }
    )
    existing.add(key)
    return True


def main() -> None:
    entities = load_jsonl(ENTITIES_PATH)
    relationships = load_jsonl(RELATIONSHIPS_PATH)
    entities_by_uid = {str(row.get("uid")): row for row in entities if row.get("uid")}

    methods = [row for row in entities if row.get("type") == "Method" or row.get("_label") == "Method"]
    examples_by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    existing_rels: set[tuple[str, str, str]] = set()
    for rel in relationships:
        from_uid = str(rel.get("from_uid") or rel.get("_from_uid") or "")
        to_uid = str(rel.get("to_uid") or rel.get("_to_uid") or "")
        rel_type = str(rel.get("type") or rel.get("_type") or "")
        existing_rels.add((from_uid, to_uid, rel_type))
        if rel_type == "HAS_EXAMPLE" and from_uid and to_uid in entities_by_uid:
            examples_by_method[from_uid].append(entities_by_uid[to_uid])

    normalized_examples = sum(1 for row in entities if normalize_example(row))

    for topic in entities:
        if topic.get("type") == "Topic" or topic.get("_label") == "Topic":
            if not str(topic.get("description") or "").strip():
                title = str(topic.get("title") or topic.get("uid") or "тема").strip()
                topic["description"] = f"Тема «{title}»: ключевые понятия, типовые приёмы решения и практическое применение в задачах."
                topic["updated_at"] = NOW

    added_examples = 0
    added_relationships = 0
    method_uids = sorted((str(m.get("uid")) for m in methods if m.get("uid")), key=len, reverse=True)

    # Hand-curated repair for the method that exposed the bug in production.
    method = entities_by_uid.get("MET-7-PREDSTAVIT-KAK-DROB")
    if method:
        for uid, patch in PREDSTAVIT_MATRIX.items():
            payload = {
                "tenant_id": TENANT_ID,
                "uid": uid,
                "created_at": str(entities_by_uid.get(uid, {}).get("created_at") or NOW),
                "updated_at": NOW,
                "lifecycle_status": "ACTIVE",
                "type": "Example",
                "_label": "Example",
                "answer_type": "symbolic_expression",
                "user_class_min": method.get("user_class_min"),
                "user_class_max": method.get("user_class_max"),
                "hints": [] if str(patch["statement"]).lower().startswith("самостоятельно:") else make_hints(patch["statement"], "symbolic_expression"),
                **patch,
            }
            before_exists = uid in entities_by_uid
            upsert_example(entities, entities_by_uid, payload)
            if not before_exists:
                added_examples += 1
            if ensure_relationship(relationships, existing_rels, method["uid"], uid):
                added_relationships += 1
        method["answer_type"] = "symbolic_expression"
        method["updated_at"] = NOW
        examples_by_method[method["uid"]] = [entities_by_uid[uid] for uid in PREDSTAVIT_MATRIX]

    for method in methods:
        method_uid = str(method.get("uid") or "")
        if not method_uid:
            continue
        examples = examples_by_method.get(method_uid, [])
        for ex in examples:
            normalize_example(ex)
        method_answer_type = str(method.get("answer_type") or "").strip()
        if examples and (not method_answer_type or method_answer_type == "text"):
            method["answer_type"] = next(
                (
                    str(ex.get("answer_type"))
                    for ex in examples
                    if str(ex.get("answer_type") or "").strip()
                    and str(ex.get("answer_type") or "").strip() != "text"
                ),
                "symbolic_expression",
            )
            method["updated_at"] = NOW

        slots: dict[tuple[str, int], dict[str, Any]] = {}
        for ex in examples:
            slot = slot_for_example(ex)
            if slot and slot not in slots:
                slots[slot] = ex

        source = next((ex for ex in examples if normalize_answer(ex.get("answer") or "")), examples[0] if examples else None)
        required_slots = [("i", 0), ("we", 1), ("we", 2), ("we", 3), ("you", 1), ("you", 2), ("you", 3)]
        for stage, difficulty in required_slots:
            if (stage, difficulty) in slots:
                continue
            new_example = clone_for_slot(method, source, stage, difficulty)
            before_exists = new_example["uid"] in entities_by_uid
            inserted = upsert_example(entities, entities_by_uid, new_example)
            normalize_example(inserted)
            slots[(stage, difficulty)] = inserted
            examples.append(inserted)
            if not before_exists:
                added_examples += 1
            if ensure_relationship(relationships, existing_rels, method_uid, inserted["uid"]):
                added_relationships += 1

        if method_uid != "MET-7-PREDSTAVIT-KAK-DROB":
            for stage, difficulty in required_slots:
                existing = slots.get((stage, difficulty))
                if not existing or "-READY20-" not in str(existing.get("uid") or ""):
                    continue
                preferred_source = (
                    slots.get(("we", difficulty))
                    if stage == "you"
                    else slots.get(("we", 1)) or source
                )
                if not preferred_source or preferred_source is existing:
                    continue
                refreshed = clone_for_slot(method, preferred_source, stage, difficulty)
                refreshed["uid"] = existing["uid"]
                refreshed["created_at"] = existing.get("created_at") or refreshed["created_at"]
                existing.update(refreshed)
                existing["updated_at"] = NOW
                normalize_example(existing)

    restored_prefix_relationships = 0
    for example in (row for row in entities if row.get("type") == "Example" or row.get("_label") == "Example"):
        example_uid = str(example.get("uid") or "")
        if not example_uid.startswith("EX-"):
            continue
        for method_uid in method_uids:
            if example_uid.startswith(f"EX-{method_uid}"):
                if ensure_relationship(relationships, existing_rels, method_uid, example_uid):
                    restored_prefix_relationships += 1
                break

    write_jsonl(ENTITIES_PATH, entities)
    write_jsonl(RELATIONSHIPS_PATH, relationships)
    print(
        "ready2.0 example normalization complete: "
        f"normalized_examples={normalized_examples}, "
        f"added_examples={added_examples}, "
        f"added_relationships={added_relationships}, "
        f"restored_prefix_relationships={restored_prefix_relationships}, "
        f"entities={len(entities)}, relationships={len(relationships)}"
    )


if __name__ == "__main__":
    main()
