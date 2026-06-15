#!/usr/bin/env python3
"""
Seed script: школьные квартальные учебные планы (RU-SCHOOL-MATH-G{grade}).

Создаёт квартально-размеченные планы по математике для целей
«Подтянуть четвертную оценку» (improve_grade).

ЖЁСТКОЕ ОГРАНИЧЕНИЕ
-------------------
Узлы плана ссылаются ТОЛЬКО на уже существующие канонические темы графа БЗ.
Источник истины пула тем — app/services/kb/graph_entities.jsonl. Новые темы
НЕ создаются. UID, отсутствующий в пуле (или явный sentinel ``MISSING``),
пропускается с предупреждением — фиктивный узел не создаётся.
Дополнительно проверяется согласованность класса плана с грейд-границами темы
(user_class_min <= G <= user_class_max).

Матрица «класс -> четверть -> существующие TOP-* UID» собрана из
grade-specific тем графа (см. вывод inventory). Темы программы, которых нет в
графе, помечены ``MISSING`` и будут добавлены при наполнении KB.

Использование (внутри контейнера):
    python /app/scripts/seed_school_curricula.py [--dry-run] [--wipe]

Идемпотентно: повторный запуск обновляет записи, не дублируя их.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings  # noqa: E402

# ---------------------------------------------------------------------------
# Матрица «класс -> [(четверть, "UID UID ...")]».
# Только существующие grade-specific UID графа. ``MISSING`` => тема программы
# отсутствует в графе и пропускается (узел не создаётся).
# ---------------------------------------------------------------------------

SCHOOL_QUARTER_TOPIC_UIDS = {
    "RU-SCHOOL-MATH-G7": [
        (1, "TOP-7-RATSIONALNYE-CHISLA TOP-7-TOZHDESTVENNYE-PREOBRAZOVANIYA TOP-TOCHKA-I-PRYAMAYA-291b4a"),
        (2, "TOP-7-STEPEN-S-NATURALNYM-POKAZATELEM TOP-7-ODNOCHLENY TOP-TREUGOLNIKI-OSNOVY-RAVENSTVO"),
        (3, "TOP-7-MNOGOCHLENY-SUMMA-I-RAZNOST TOP-7-FORMULY-SOKRASHCHENNOGO-UMNOZHENIYA TOP-7-RATSIONALNYE-VYRAZHENIYA"),
        (4, "TOP-7-FUNKCII-I-GRAFIKI TOP-GRAFIK-FUNKTSII-61637e TOP-7-LINEJNYE-URAVNENIYA-S-DVUMYA-PEREMENNYMI"),
    ],
    "RU-SCHOOL-MATH-G8": [
        (1, "TOP-8-PROIZVEDENIE-I-CHASTNOE-DROBEJ TOP-8-SUMMA-I-RAZNOST-RACIONALNYH-DROBEJ TOP-OBRATNAYA-PROPORCIONALNOST-Y-RAVNO-K-NA-X-20260328"),
        (2, "TOP-8-ARIFMETICHESKIJ-KVADRATNYJ-KOREN TOP-8-SVOYSTVA-KVADRATNOGO-KORNYA TOP-8-PREOBRAZOVANIE-VYRAZHENIJ-S-KORNYAMI TOP-TEOREMA-PIFAGORA"),
        (3, "TOP-KVADRATNYE-URAVNENIYA-0fdb01 TOP-8-STEPEN-S-CELYM-POKAZATELEM TOP-8-STANDARTNYJ-VID-CHISLA"),
        (4, "TOP-8-CHISLOVYE-NERAVENSTVA-I-SVOYSTVA TOP-8-FUNKCIYA-I-EE-SVOYSTVA TOP-8-SVOYSTVA-NEKOTORYH-VIDOV-FUNKCIJ"),
    ],
    "RU-SCHOOL-MATH-G9": [
        (1, "TOP-9-KVADRATICHNAYA-FUNKCIYA-I-GRAFIK TOP-9-FUNKCII-I-IX-SVOYSTVA"),
        (2, "TOP-9-NERAVENSTVA-I-SISTEMY-S-DVUMYA-PEREMENNYMI-20260322 TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM"),
        (3, "TOP-9-ARIFMETICHESKAYA-PROGRESSIYA TOP-9-GP"),
        (4, "TOP-9-ELEMENTY-KOMBINATORIKI TOP-RESHENIE-TREUGOLNIKOV TOP-NEW-CIRCLE-EQUATION"),
    ],
}

# Класс, к которому относится план (для согласования с грейд-границами темы).
CURRICULUM_GRADE = {
    "RU-SCHOOL-MATH-G7": 7,
    "RU-SCHOOL-MATH-G8": 8,
    "RU-SCHOOL-MATH-G9": 9,
}

CURRICULUM_TITLES = {
    "RU-SCHOOL-MATH-G7": "Школьная программа: Математика, 7 класс",
    "RU-SCHOOL-MATH-G8": "Школьная программа: Математика, 8 класс",
    "RU-SCHOOL-MATH-G9": "Школьная программа: Математика, 9 класс",
}


# ---------------------------------------------------------------------------
# Пул существующих тем (источник истины) + валидация
# ---------------------------------------------------------------------------

def _load_topic_pool() -> dict:
    """Return {uid: (user_class_min, user_class_max)} from graph_entities.jsonl."""
    path = Path(__file__).parent.parent / "app/services/kb/graph_entities.jsonl"
    pool: dict[str, tuple] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            uid = str(e.get("uid") or "")
            is_topic = str(e.get("type") or e.get("_label")).lower() == "topic" or uid.startswith("TOP-")
            if not is_topic or not uid:
                continue
            pool[uid] = (e.get("user_class_min"), e.get("user_class_max"))
    return pool


def _grade_band_ok(grade: int, band: tuple) -> bool:
    mn, mx = band
    lo = mn if mn is not None else 2
    hi = mx if mx is not None else 11
    return lo <= grade <= hi


def _build_nodes(code: str, rows, pool: dict, warnings: list) -> list:
    """Build validated curriculum nodes (only existing, grade-consistent UIDs)."""
    grade = CURRICULUM_GRADE[code]
    nodes: list[dict] = []
    order = 0
    seen: set[str] = set()
    for quarter, uid_cell in rows:
        uid_cell = (uid_cell or "").strip()
        if not uid_cell or uid_cell == "MISSING":
            continue
        for uid in uid_cell.split():
            if uid == "MISSING" or not uid:
                continue
            if uid in seen:
                continue
            if uid not in pool:
                warnings.append(f"{code} q{quarter}: UID отсутствует в пуле тем — пропуск: {uid}")
                continue
            if not _grade_band_ok(grade, pool[uid]):
                warnings.append(
                    f"{code} q{quarter}: UID {uid} не согласован с классом {grade} "
                    f"(band={pool[uid]}) — пропуск"
                )
                continue
            seen.add(uid)
            order += 1
            nodes.append({"kind": "topic", "canonical_uid": uid, "order_index": order, "quarter": quarter})
    return nodes


# ---------------------------------------------------------------------------
# DB helpers (по образцу seed_curricula.py)
# ---------------------------------------------------------------------------

def _get_conn():
    try:
        import psycopg2
        dsn = str(settings.pg_dsn) if settings.pg_dsn else ""
        if not dsn:
            return None
        return psycopg2.connect(dsn)
    except Exception as exc:
        print(f"  [ERROR] Cannot connect to PostgreSQL: {exc}")
        return None


def _upsert_curriculum(cur, code: str, title: str) -> int:
    cur.execute("SELECT id FROM curricula WHERE code = %s", (code,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE curricula SET title=%s, standard=%s, language=%s, status=%s WHERE code=%s",
            (title, "ФГОС", "ru", "active", code),
        )
        return row[0]
    cur.execute(
        "INSERT INTO curricula(code, title, standard, language, status) "
        "VALUES (%s,%s,'ФГОС','ru','active') RETURNING id",
        (code, title),
    )
    return cur.fetchone()[0]


def _upsert_nodes(cur, curriculum_id: int, nodes: list) -> int:
    cur.execute("DELETE FROM curriculum_nodes WHERE curriculum_id = %s", (curriculum_id,))
    count = 0
    for n in nodes:
        cur.execute(
            "INSERT INTO curriculum_nodes"
            "(curriculum_id, kind, canonical_uid, order_index, is_required, quarter) "
            "VALUES (%s, 'topic', %s, %s, TRUE, %s)",
            (curriculum_id, n["canonical_uid"], n["order_index"], n["quarter"]),
        )
        count += 1
    return count


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

def seed(dry_run: bool = False, wipe: bool = False) -> None:
    pool = _load_topic_pool()
    print(f"Пул существующих тем: {len(pool)} UID (источник graph_entities.jsonl)")

    warnings: list[str] = []
    plans = []
    for code, rows in SCHOOL_QUARTER_TOPIC_UIDS.items():
        nodes = _build_nodes(code, rows, pool, warnings)
        plans.append((code, CURRICULUM_TITLES[code], nodes))

    for w in warnings:
        print(f"  [WARN] {w}")

    conn = _get_conn()
    if conn is None:
        print("PostgreSQL не настроен — печатаем план (dry).")
        for code, title, nodes in plans:
            print(f"  {code}: {len(nodes)} узлов")
            for n in nodes:
                print(f"        q{n['quarter']} #{n['order_index']:2d} {n['canonical_uid']}")
        return

    total_curricula = 0
    total_nodes = 0
    try:
        with conn:
            with conn.cursor() as cur:
                if wipe:
                    codes = tuple(SCHOOL_QUARTER_TOPIC_UIDS.keys())
                    if dry_run:
                        print(f"  [DRY] WIPE: удалили бы планы {codes}")
                    else:
                        cur.execute(
                            "DELETE FROM curriculum_nodes WHERE curriculum_id IN "
                            "(SELECT id FROM curricula WHERE code = ANY(%s))",
                            (list(codes),),
                        )
                        cur.execute("DELETE FROM curricula WHERE code = ANY(%s)", (list(codes),))
                        print("  [WIPE] Школьные планы удалены")

                for code, title, nodes in plans:
                    if dry_run:
                        print(f"  [DRY] {code} ({len(nodes)} узлов)")
                        for n in nodes:
                            print(f"        q{n['quarter']} #{n['order_index']:2d} {n['canonical_uid']}")
                        total_curricula += 1
                        total_nodes += len(nodes)
                        continue
                    cid = _upsert_curriculum(cur, code, title)
                    n_nodes = _upsert_nodes(cur, cid, nodes)
                    print(f"  [OK] {code} (id={cid}): {n_nodes} узлов")
                    total_curricula += 1
                    total_nodes += n_nodes
    finally:
        conn.close()

    mode = "(DRY RUN)" if dry_run else "(APPLIED)"
    print()
    print("=" * 60)
    print(f"Seed School Curricula завершён {mode}")
    print(f"  Curricula : {total_curricula}")
    print(f"  Nodes     : {total_nodes}")
    print(f"  Warnings  : {len(warnings)}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed school quarter curricula (RU-SCHOOL-MATH-G*)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--wipe", action="store_true", help="Delete school curricula before seeding")
    args = parser.parse_args()
    print("Seed School Curricula (RU-SCHOOL-MATH-G7/G8/G9)")
    print("=" * 60)
    seed(dry_run=args.dry_run, wipe=args.wipe)
