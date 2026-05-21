#!/usr/bin/env python3
"""
Seed script: создание/обновление curricula и curriculum_nodes в PostgreSQL.

Создаёт три программы по структуре ФИПИ КИМ 2026:
  RU-OGE-MATH-2026       — ОГЭ Математика, 25 заданий
  RU-EGE-BASE-MATH-2026  — ЕГЭ Базовый, 21 задание
  RU-EGE-PROF-MATH-2026  — ЕГЭ Профиль, 19 заданий

Темы соответствуют актуальному пулу тем графа БЗ и матрице
«экзамен -> номер задания -> UID темы».

Использование (внутри контейнера):
    python /app/scripts/seed_curricula.py [--dry-run]

Скрипт идемпотентен: при повторном запуске обновляет существующие записи,
не дублирует их.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings  # noqa: E402

# ---------------------------------------------------------------------------
# Определения curricula — матрица «экзамен -> задание -> UID темы».
# MISSING означает, что тема требуется спецификацией, но отсутствует в пуле
# готовых тем, поэтому фиктивная запись в curriculum_nodes не создается.
# ---------------------------------------------------------------------------

EXAM_TASK_TOPIC_UIDS = {
    "RU-OGE-MATH-2026": [
        ("1", "TOP-7-RATSIONALNYE-CHISLA TOP-DEJSTVITELNYE-CHISLA-b50b77 TOP-OKRUGLENIE-CHISEL-20260328 TOP-PLOSCHADI-c811e2"),
        ("2", "TOP-7-RATSIONALNYE-CHISLA TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-PLOSCHADI-c811e2"),
        ("3", "TOP-7-RATSIONALNYE-CHISLA TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-PLOSCHADI-c811e2"),
        ("4", "TOP-7-RATSIONALNYE-CHISLA TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-PLOSCHADI-c811e2"),
        ("5", "TOP-11-STATISTIKA-I-ANALIZ-DANNYH TOP-SREDNEE-ARIFMETICHESKOE-20260328"),
        ("6", "TOP-6-POLOZHITELNYE-I-OTRITSATELNYE-CHISLA TOP-TSELYE-CHISLA-23a63f TOP-7-RATSIONALNYE-CHISLA TOP-6-DEJSTVIYA-SO-SMESHANNYMI-CHISLAMI"),
        ("7", "TOP-7-RATSIONALNYE-CHISLA TOP-OKRUGLENIE-CHISEL-20260328 TOP-8-STANDARTNYJ-VID-CHISLA"),
        ("8", "TOP-PEREMENNYE-I-VYRAZHENIYA-3652b0 TOP-7-TOZHDESTVENNYE-PREOBRAZOVANIYA TOP-7-FORMULY-SOKRASHCHENNOGO-UMNOZHENIYA TOP-7-FAKTORIZACIYA-MNOGOCHLENOV TOP-DEJSTVIYA-S-MNOGOCHLENAMI-20260328 TOP-7-RATSIONALNYE-VYRAZHENIYA"),
        ("9", "TOP-LINEJNYE-URAVNENIYA-94fc09 TOP-KVADRATNYE-URAVNENIYA-0fdb01 TOP-7-SISTEMY-LINEJNYH-URAVNENIJ TOP-SISTEMY-URAVNENIJ-118b3a"),
        ("10", "TOP-VEROYATNOST-d3cd07 TOP-OSNOVY-TEORII-VEROYATNOS-c8e176"),
        ("11", "TOP-7-FUNKCII-I-GRAFIKI TOP-GRAFIK-FUNKTSII-61637e TOP-LINEJNYE-FUNKTSII-270099 TOP-9-KVADRATICHNAYA-FUNKCIYA-I-GRAFIK TOP-8-FUNKCIYA-I-EE-SVOYSTVA TOP-OBLAST-OPREDELENIYA-e36f26 TOP-MONOTONNOST-dbe010"),
        ("12", "TOP-8-ARIFMETICHESKIJ-KVADRATNYJ-KOREN TOP-8-SVOYSTVA-KVADRATNOGO-KORNYA TOP-8-PREOBRAZOVANIE-VYRAZHENIJ-S-KORNYAMI TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM TOP-7-RATSIONALNYE-VYRAZHENIYA"),
        ("13", "TOP-8-CHISLOVYE-NERAVENSTVA-I-SVOYSTVA TOP-LINEJNYE-NERAVENSTVA-f61cf0 TOP-KVADRATNYE-NERAVENSTVA-f1ebc9 TOP-RATSIONALNYE-NERAVENSTVA-0c5460 TOP-SISTEMY-NERAVENSTV-ODNA-PEREMENNAYA-20260328 TOP-CHISLOVYE-PROMEZHUTKI-20260328"),
        ("14", "TOP-9-ARIFMETICHESKAYA-PROGRESSIYA TOP-9-GP"),
        ("15", "TOP-TREUGOLNIKI-OSNOVY-RAVENSTVO TOP-TEOREMA-PIFAGORA TOP-PLOSHCHAD-TREUGOLNIKA-20260328 TOP-PLOSCHADI-c811e2"),
        ("16", "TOP-6-SIMMETRIYA-I-KRUG TOP-VPISANNYE-I-OPISANNYE-OKRUZHNOSTI-20260328 TOP-PODOBIE-86fb4a"),
        ("17", "TOP-RESHENIE-TREUGOLNIKOV TOP-PODOBIE-86fb4a TOP-PLOSCHADI-c811e2"),
        ("18", "TOP-TOCHKA-I-PRYAMAYA-291b4a TOP-PLOSCHADI-c811e2 TOP-TEOREMA-PIFAGORA"),
        ("19", "TOP-8-CHISLOVYE-NERAVENSTVA-I-SVOYSTVA TOP-CHISLOVYE-PROMEZHUTKI-20260328 TOP-TOCHKA-I-PRYAMAYA-291b4a"),
        ("20", "TOP-KVADRATNYE-URAVNENIYA-0fdb01 TOP-RATSIONALNYE-URAVNENIYA-e5c010 TOP-IRRATSIONALNYE-URAVNENIYA-e5dde5 TOP-10-RAVNOSILNYE-UR-I-NER TOP-7-FAKTORIZACIYA-MNOGOCHLENOV"),
        ("21", "TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-SISTEMY-URAVNENIJ-118b3a TOP-OBRATNAYA-PROPORCIONALNOST-Y-RAVNO-K-NA-X-20260328"),
        ("22", "TOP-9-FUNKCII-I-IX-SVOYSTVA TOP-GRAFIK-FUNKTSII-61637e TOP-MONOTONNOST-dbe010 TOP-OBLAST-OPREDELENIYA-e36f26"),
        ("23", "TOP-PLOSCHADI-c811e2 TOP-PLOSHCHAD-TREUGOLNIKA-20260328 TOP-TEOREMA-PIFAGORA TOP-6-SIMMETRIYA-I-KRUG"),
        ("24", "TOP-TREUGOLNIKI-OSNOVY-RAVENSTVO TOP-PODOBIE-86fb4a TOP-VPISANNYE-I-OPISANNYE-OKRUZHNOSTI-20260328"),
        ("25", "TOP-TREUGOLNIKI-OSNOVY-RAVENSTVO TOP-RESHENIE-TREUGOLNIKOV TOP-PODOBIE-86fb4a TOP-VPISANNYE-I-OPISANNYE-OKRUZHNOSTI-20260328"),
    ],
    "RU-EGE-BASE-MATH-2026": [
        ("1", "TOP-7-RATSIONALNYE-CHISLA TOP-DEJSTVITELNYE-CHISLA-b50b77 TOP-8-STANDARTNYJ-VID-CHISLA TOP-OKRUGLENIE-CHISEL-20260328 TOP-8-ARIFMETICHESKIJ-KVADRATNYJ-KOREN TOP-8-SVOYSTVA-KVADRATNOGO-KORNYA TOP-8-STEPEN-S-CELYM-POKAZATELEM TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM"),
        ("2", "TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-7-RATSIONALNYE-CHISLA TOP-OKRUGLENIE-CHISEL-20260328 TOP-PLOSCHADI-c811e2"),
        ("3", "TOP-11-STATISTIKA-I-ANALIZ-DANNYH TOP-SREDNIE-HARAKTERISTIKI-b231f6 TOP-SREDNEE-ARIFMETICHESKOE-20260328"),
        ("4", "TOP-PEREMENNYE-I-VYRAZHENIYA-3652b0 TOP-7-RATSIONALNYE-VYRAZHENIYA TOP-7-TOZHDESTVENNYE-PREOBRAZOVANIYA TOP-7-FORMULY-SOKRASHCHENNOGO-UMNOZHENIYA TOP-8-KVADRATNYJ-TREHCHLEN"),
        ("5", "TOP-VEROYATNOST-d3cd07 TOP-OSNOVY-TEORII-VEROYATNOS-c8e176"),
        ("6", "TOP-11-STATISTIKA-I-ANALIZ-DANNYH TOP-GRAFIK-FUNKTSII-61637e"),
        ("7", "TOP-9-FUNKCII-I-IX-SVOYSTVA TOP-GRAFIK-FUNKTSII-61637e TOP-OBLAST-OPREDELENIYA-e36f26 TOP-MONOTONNOST-dbe010 TOP-PROIZVODNAYA-cfd26d TOP-PRAVILA-DIFFERENTSIROVANIYA-3bd912 TOP-11-GEOMETRICHESKIJ-SMYSL-PROIZVODNOJ TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f"),
        ("8", "TOP-9-MATEMATICHESKAYA-INDUKCIYA TOP-8-CHISLOVYE-NERAVENSTVA-I-SVOYSTVA TOP-CHISLOVYE-PROMEZHUTKI-20260328"),
        ("9", "TOP-TREUGOLNIKI-OSNOVY-RAVENSTVO TOP-TEOREMA-PIFAGORA TOP-PLOSHCHAD-TREUGOLNIKA-20260328 TOP-PLOSCHADI-c811e2"),
        ("10", "TOP-6-SIMMETRIYA-I-KRUG TOP-VPISANNYE-I-OPISANNYE-OKRUZHNOSTI-20260328 TOP-PODOBIE-86fb4a"),
        ("11", "TOP-OBYOMY-MNOGOGRANNIKOV-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-MNOGOGRANNIKOV-20260328 TOP-OBYOMY-TEL-VRASCHENIYA-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-TEL-VRASCHENIYA-20260328 TOP-KOMBINATSII-TEL-I-PRINTSIP-KAVALERI-20260328"),
        ("12", "TOP-PODOBIE-86fb4a TOP-RESHENIE-TREUGOLNIKOV TOP-PLOSCHADI-c811e2"),
        ("13", "TOP-OBYOMY-MNOGOGRANNIKOV-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-MNOGOGRANNIKOV-20260328 TOP-OBYOMY-TEL-VRASCHENIYA-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-TEL-VRASCHENIYA-20260328"),
        ("14", "TOP-7-RATSIONALNYE-VYRAZHENIYA TOP-8-KVADRATNYJ-TREHCHLEN TOP-8-ARIFMETICHESKIJ-KVADRATNYJ-KOREN TOP-8-PREOBRAZOVANIE-VYRAZHENIJ-S-KORNYAMI TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea"),
        ("15", "TOP-7-RATSIONALNYE-CHISLA TOP-DEJSTVITELNYE-CHISLA-b50b77 TOP-8-STEPEN-S-CELYM-POKAZATELEM TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM TOP-MODUL-CHISLA-20260328"),
        ("16", "TOP-8-PREOBRAZOVANIE-VYRAZHENIJ-S-KORNYAMI TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea TOP-10-POKAZATELNAYA-FUNKCIYA TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM"),
        ("17", "TOP-KVADRATNYE-URAVNENIYA-0fdb01 TOP-RATSIONALNYE-URAVNENIYA-e5c010 TOP-IRRATSIONALNYE-URAVNENIYA-e5dde5 TOP-10-POKAZATELNYE-URAVNENIYA TOP-10-TRIGONOMETRICHESKIE-FORMULY TOP-TRIGONOMETRICHESKIE-URAVNENIYA-37c238 TOP-10-TRIG-URAVNENIYA-I-NERAVENSTVA TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea"),
        ("18", "TOP-LINEJNYE-NERAVENSTVA-f61cf0 TOP-KVADRATNYE-NERAVENSTVA-f1ebc9 TOP-RATSIONALNYE-NERAVENSTVA-0c5460 TOP-IRRATSIONALNYE-NERAVENSTVA TOP-10-POKAZATELNYE-NERAVENSTVA TOP-LOGARIFMICHESKIE-NERAVENSTVA TOP-TRIGONOMETRICHESKIE-NERAVENSTV-a65a77"),
        ("19", "TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-7-RATSIONALNYE-CHISLA TOP-DEJSTVITELNYE-CHISLA-b50b77 TOP-OKRUGLENIE-CHISEL-20260328"),
        ("20", "TOP-9-ARIFMETICHESKAYA-PROGRESSIYA TOP-9-GP TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-LINEJNYE-URAVNENIYA-94fc09 TOP-KVADRATNYE-URAVNENIYA-0fdb01"),
        ("21", "TOP-7-RATSIONALNYE-VYRAZHENIYA TOP-8-KVADRATNYJ-TREHCHLEN TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f TOP-PROIZVODNAYA-cfd26d"),
    ],
    "RU-EGE-PROF-MATH-2026": [
        ("1", "TOP-TREUGOLNIKI-OSNOVY-RAVENSTVO TOP-PODOBIE-86fb4a TOP-TEOREMA-PIFAGORA TOP-PLOSCHADI-c811e2 TOP-PLOSHCHAD-TREUGOLNIKA-20260328 TOP-6-SIMMETRIYA-I-KRUG TOP-VPISANNYE-I-OPISANNYE-OKRUZHNOSTI-20260328 TOP-RESHENIE-TREUGOLNIKOV"),
        ("2", "MISSING"),
        ("3", "TOP-OBYOMY-MNOGOGRANNIKOV-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-MNOGOGRANNIKOV-20260328 TOP-OBYOMY-TEL-VRASCHENIYA-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-TEL-VRASCHENIYA-20260328 TOP-KOMBINATSII-TEL-I-PRINTSIP-KAVALERI-20260328"),
        ("4", "TOP-VEROYATNOST-d3cd07 TOP-OSNOVY-TEORII-VEROYATNOS-c8e176"),
        ("5", "TOP-9-ELEMENTY-KOMBINATORIKI TOP-11-KOMBINATORIKA-I-BINOM-NYUTONA TOP-VEROYATNOST-d3cd07 TOP-OSNOVY-TEORII-VEROYATNOS-c8e176"),
        ("6", "TOP-KVADRATNYE-URAVNENIYA-0fdb01 TOP-RATSIONALNYE-URAVNENIYA-e5c010 TOP-7-SISTEMY-LINEJNYH-URAVNENIJ TOP-SISTEMY-URAVNENIJ-118b3a TOP-10-RAVNOSILNYE-UR-I-NER"),
        ("7", "TOP-7-RATSIONALNYE-VYRAZHENIYA TOP-8-STEPEN-S-CELYM-POKAZATELEM TOP-9-STEPEN-S-RACIONALNYM-POKAZATELEM TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea TOP-10-POKAZATELNAYA-FUNKCIYA TOP-KORNEVYE-FUNKTSII-2a9a47 TOP-8-ARIFMETICHESKIJ-KVADRATNYJ-KOREN TOP-8-PREOBRAZOVANIE-VYRAZHENIJ-S-KORNYAMI"),
        ("8", "TOP-PROIZVODNAYA-cfd26d TOP-PRAVILA-DIFFERENTSIROVANIYA-3bd912 TOP-11-GEOMETRICHESKIJ-SMYSL-PROIZVODNOJ TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f TOP-PERVOOBRAZNAYA-e23096 TOP-OPREDELYONNYJ-INTEGRAL-2f73d5 TOP-PRIMENENIYA-INTEGRALA-d4e675"),
        ("9", "TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-LINEJNYE-URAVNENIYA-94fc09 TOP-KVADRATNYE-URAVNENIYA-0fdb01 TOP-10-RAVNOSILNYE-UR-I-NER"),
        ("10", "TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-OBRATNAYA-PROPORCIONALNOST-Y-RAVNO-K-NA-X-20260328 TOP-9-ARIFMETICHESKAYA-PROGRESSIYA TOP-9-GP"),
        ("11", "TOP-9-FUNKCII-I-IX-SVOYSTVA TOP-GRAFIK-FUNKTSII-61637e TOP-OBLAST-OPREDELENIYA-e36f26 TOP-MONOTONNOST-dbe010 TOP-9-KVADRATICHNAYA-FUNKCIYA-I-GRAFIK TOP-RATSIONALNYE-FUNKTSII-677ea5 TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea TOP-10-POKAZATELNAYA-FUNKCIYA TOP-TRIGONOMETRICHESKIE-FUNKTSII-84c00c"),
        ("12", "TOP-PROIZVODNAYA-cfd26d TOP-PRAVILA-DIFFERENTSIROVANIYA-3bd912 TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f TOP-MONOTONNOST-dbe010"),
        ("13", "TOP-RADIANNAYA-MERA-51263f TOP-TRIGONOMETRICHESKIE-FUNKTSII-84c00c TOP-10-TRIGONOMETRICHESKIE-FORMULY TOP-TRIGONOMETRICHESKIE-URAVNENIYA-37c238 TOP-10-TRIG-URAVNENIYA-I-NERAVENSTVA TOP-TRIGONOMETRICHESKIE-NERAVENSTV-a65a77"),
        ("14", "TOP-OBYOMY-MNOGOGRANNIKOV-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-MNOGOGRANNIKOV-20260328 TOP-OBYOMY-TEL-VRASCHENIYA-20260328 TOP-PLOSCHADI-POVERHNOSTEJ-TEL-VRASCHENIYA-20260328 TOP-KOMBINATSII-TEL-I-PRINTSIP-KAVALERI-20260328"),
        ("15", "TOP-10-POKAZATELNYE-URAVNENIYA TOP-10-POKAZATELNYE-NERAVENSTVA TOP-LOGARIFMICHESKIE-NERAVENSTVA TOP-IRRATSIONALNYE-URAVNENIYA-e5dde5 TOP-IRRATSIONALNYE-NERAVENSTVA TOP-RATSIONALNYE-NERAVENSTVA-0c5460 TOP-NERAVENSTVA-S-MODULEM-102864 TOP-10-RAVNOSILNYE-UR-I-NER"),
        ("16", "TOP-9-GP TOP-5-VYRAZHENIYA-I-URAVNENIYA TOP-DEJSTVITELNYE-CHISLA-b50b77 TOP-OKRUGLENIE-CHISEL-20260328"),
        ("17", "TOP-TREUGOLNIKI-OSNOVY-RAVENSTVO TOP-PODOBIE-86fb4a TOP-RESHENIE-TREUGOLNIKOV TOP-6-SIMMETRIYA-I-KRUG TOP-VPISANNYE-I-OPISANNYE-OKRUZHNOSTI-20260328 TOP-PLOSCHADI-c811e2"),
        ("18", "TOP-EGE-ZADACHI-S-PARAMETROM-2026 TOP-10-RAVNOSILNYE-UR-I-NER TOP-7-TOZHDESTVENNYE-PREOBRAZOVANIYA TOP-9-FUNKCII-I-IX-SVOYSTVA"),
        ("19", "TOP-TSELYE-CHISLA-23a63f TOP-MODUL-CHISLA-20260328 TOP-9-MATEMATICHESKAYA-INDUKCIYA TOP-8-CHISLOVYE-NERAVENSTVA-I-SVOYSTVA TOP-CHISLOVYE-PROMEZHUTKI-20260328"),
    ],
}


def _nodes_from_task_rows(rows: list[tuple[str, str]]) -> list[dict]:
    """Build one curriculum node per UID, collecting all exam task numbers."""
    tasks_by_uid: dict[str, list[str]] = {}
    for task, uid_cell in rows:
        uid_cell = uid_cell.strip()
        if not uid_cell or uid_cell == "MISSING":
            continue
        for uid in uid_cell.split():
            if uid == "MISSING":
                continue
            tasks_by_uid.setdefault(uid, [])
            if task not in tasks_by_uid[uid]:
                tasks_by_uid[uid].append(task)

    return [
        {"order": order, "uid": uid, "task": ",".join(tasks)}
        for order, (uid, tasks) in enumerate(tasks_by_uid.items(), 1)
    ]


CURRICULA = [
    {
        "code": "RU-OGE-MATH-2026",
        "title": "ОГЭ Математика 2026",
        "standard": "ОГЭ",
        "language": "ru",
        "status": "active",
        "nodes": _nodes_from_task_rows(EXAM_TASK_TOPIC_UIDS["RU-OGE-MATH-2026"]),
    },
    {
        "code": "RU-EGE-BASE-MATH-2026",
        "title": "ЕГЭ Базовый Математика 2026",
        "standard": "ЕГЭ Базовый",
        "language": "ru",
        "status": "active",
        "nodes": _nodes_from_task_rows(EXAM_TASK_TOPIC_UIDS["RU-EGE-BASE-MATH-2026"]),
    },
    {
        "code": "RU-EGE-PROF-MATH-2026",
        "title": "ЕГЭ Профиль Математика 2026",
        "standard": "ЕГЭ Профиль",
        "language": "ru",
        "status": "active",
        "nodes": _nodes_from_task_rows(EXAM_TASK_TOPIC_UIDS["RU-EGE-PROF-MATH-2026"]),
    },
]


# ---------------------------------------------------------------------------
# Вспомогательные функции
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


def _upsert_curriculum(cur, code: str, title: str, standard: str,
                       language: str, status: str) -> int:
    """INSERT or UPDATE curriculum; returns curriculum id."""
    cur.execute("SELECT id FROM curricula WHERE code = %s", (code,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE curricula SET title=%s, standard=%s, language=%s, status=%s WHERE code=%s",
            (title, standard, language, status, code),
        )
        return row[0]
    else:
        cur.execute(
            "INSERT INTO curricula(code, title, standard, language, status) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (code, title, standard, language, status),
        )
        return cur.fetchone()[0]


def _upsert_nodes(cur, curriculum_id: int, nodes: list) -> int:
    """Replace all curriculum_nodes for this curriculum."""
    cur.execute("DELETE FROM curriculum_nodes WHERE curriculum_id = %s", (curriculum_id,))
    count = 0
    for n in nodes:
        cur.execute(
            "INSERT INTO curriculum_nodes"
            "(curriculum_id, kind, canonical_uid, order_index, is_required, exam_task_number) "
            "VALUES (%s, 'topic', %s, %s, TRUE, %s)",
            (curriculum_id, n["uid"], n["order"], n.get("task")),
        )
        count += 1
    return count


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

def seed(dry_run: bool = False, wipe: bool = False) -> None:
    conn = _get_conn()
    if conn is None:
        print("PostgreSQL не настроен — пропускаем seeding curriculum.")
        return

    total_curricula = 0
    total_nodes = 0

    try:
        with conn:
            with conn.cursor() as cur:
                if wipe:
                    if dry_run:
                        cur.execute("SELECT count(*) FROM curriculum_nodes")
                        n_nodes = cur.fetchone()[0]
                        cur.execute("SELECT count(*) FROM curricula")
                        n_cur = cur.fetchone()[0]
                        print(f"  [DRY] WIPE: удалили бы {n_nodes} узлов и {n_cur} курикулумов")
                    else:
                        cur.execute("DELETE FROM curriculum_nodes")
                        cur.execute("DELETE FROM curricula")
                        print("  [WIPE] Все курикулумы и узлы удалены")

                for curriculum in CURRICULA:
                    code = curriculum["code"]
                    if dry_run:
                        print(f"  [DRY] curriculum: {code} ({len(curriculum['nodes'])} topics)")
                        for n in curriculum["nodes"]:
                            print(f"        {n['order']:2d}. {n['uid']}  task={n.get('task')}")
                        total_curricula += 1
                        total_nodes += len(curriculum["nodes"])
                        continue

                    cid = _upsert_curriculum(
                        cur,
                        code,
                        curriculum["title"],
                        curriculum["standard"],
                        curriculum["language"],
                        curriculum["status"],
                    )
                    n_nodes = _upsert_nodes(cur, cid, curriculum["nodes"])
                    print(f"  [OK] {code} (id={cid}): {n_nodes} узлов")
                    total_curricula += 1
                    total_nodes += n_nodes
    finally:
        conn.close()

    mode = "(DRY RUN)" if dry_run else "(APPLIED)"
    print()
    print(f"{'=' * 60}")
    print(f"Seed Curricula завершён {mode}")
    print(f"  Curricula : {total_curricula}")
    print(f"  Nodes     : {total_nodes}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed PostgreSQL curriculum records")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--wipe", action="store_true", help="Delete ALL curricula before seeding")
    args = parser.parse_args()

    mode_parts = []
    if args.dry_run:
        mode_parts.append("DRY RUN")
    if args.wipe:
        mode_parts.append("WIPE + RESEED")
    print("Seed Curricula (OGE / EGE-BASE / EGE-PROF)")
    print(f"Режим: {' | '.join(mode_parts) or 'WRITE'}")
    print("=" * 60)
    seed(dry_run=args.dry_run, wipe=args.wipe)
