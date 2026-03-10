#!/usr/bin/env python3
"""Migrate: set user_class_min / user_class_max on ALL existing Method nodes.

For each Topic we know the grade range from the Russian math curriculum.
The script propagates the grade range from Topic → Skill → Method via Cypher.

For topics spanning multiple grade bands (e.g. 7-11) the existing methods
keep the full range — the seed_methods_by_grade.py script separately creates
grade-specific methods with narrower ranges and textbook-aligned content.

Usage (inside KB container):
    python scripts/migrate_method_grades.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graph.neo4j_repo import Neo4jRepo  # noqa: E402

TENANT_ID = "default"

# ---------------------------------------------------------------------------
# Grade mapping: topic_uid → (user_class_min, user_class_max)
# Based on official Russian math curriculum:
#   1-4 kl: Моро М.И.
#   5-6 kl: Виленкин Н.Я., Мерзляк А.Г.
#   7-9 kl: Макарычев Ю.Н., Атанасян Л.С., Мерзляк А.Г.
#   10-11 kl: Алимов Ш.А., Колмогоров А.Н., Мордкович А.Г.
# ---------------------------------------------------------------------------
TOPIC_GRADES: dict[str, tuple[int, int]] = {
    # ── Арифметика ──────────────────────────────────────────────────────
    "TOPIC-MULT-TABLE":                        (2, 4),
    "TOPIC-FRACTIONS":                         (5, 6),
    "TOP-NATURALNYE-CHISLA-b27027":            (5, 6),
    "TOP-OPERATSII-I-SVOJSTVA-b8ac93":         (5, 6),
    "TOP-PORYADOK-DEJSTVIJ-006":               (5, 6),
    "TOP-DELIMOST-7143f5":                     (5, 6),
    "TOP-TSELYE-CHISLA-23a63f":                (5, 7),
    "TOP-RATSIONALNYE-CHISLA-dd476c":          (6, 7),

    # ── Числа и структуры ───────────────────────────────────────────────
    "TOP-EDINITSY-IZMERENIYA-002":             (5, 6),
    "TOP-TEKSTOVYE-ZADACHI-004":               (5, 9),
    "TOP-NOD-I-NOK-b29ab2":                    (5, 6),
    "TOP-PROSTYE-CHISLA-976ead":               (5, 6),
    "TOP-DEJSTVITELNYE-CHISLA-b50b77":         (8, 9),
    "TOP-KOMPLEKSNYE-CHISLA-89e957":           (10, 11),

    # ── Алгебра ─────────────────────────────────────────────────────────
    "TOP-PEREMENNYE-I-VYRAZHENIYA-3652b0":     (7, 7),
    "TOP-MNOGOCHLENY-0cd461":                  (7, 8),
    "TOP-LINEJNYE-URAVNENIYA-94fc09":          (7, 7),
    "TOP-SISTEMY-URAVNENIJ-118b3a":            (7, 9),
    "TOP-LINEJNYE-NERAVENSTVA-f61cf0":         (8, 9),
    "TOP-KVADRATNYE-URAVNENIYA-0fdb01":        (8, 9),
    "TOP-DISKRIMINANT-4c4ddb":                 (8, 9),
    "TOP-FAKTORIZATSIYA-060de7":               (7, 9),
    "TOP-KVADRATNYE-NERAVENSTVA-f1ebc9":       (8, 9),
    "TOP-RATSIONALNYE-URAVNENIYA-e5c010":      (8, 9),
    "TOP-RATSIONALNYE-NERAVENSTVA-0c5460":     (9, 9),
    "TOP-NERAVENSTVA-S-MODULEM-102864":        (9, 11),
    "TOP-IRRATSIONALNYE-URAVNENIYA-e5dde5":    (10, 11),
    "TOP-STEPENI-5a8790":                      (7, 9),
    "TOP-KORNI-542410":                        (8, 9),

    # ── Функции ─────────────────────────────────────────────────────────
    "TOP-FUNKTSIYA-KAK-OTOBRAZHENIE-1e3bb7":   (7, 8),
    "TOP-GRAFIK-FUNKTSII-61637e":              (7, 9),
    "TOP-LINEJNYE-FUNKTSII-270099":            (7, 7),
    "TOP-OBLAST-OPREDELENIYA-e36f26":          (8, 9),
    "TOP-MONOTONNOST-dbe010":                  (8, 9),
    "TOP-OBRATNAYA-FUNKTSIYA-9f767f":          (9, 11),
    "TOP-RATSIONALNYE-FUNKTSII-677ea5":        (8, 9),
    "TOP-KORNEVYE-FUNKTSII-2a9a47":            (8, 9),
    "TOP-STEPENNYE-FUNKTSII-9d2782":           (10, 11),
    "TOP-EKSPONENTSIALNYE-FUNKTSII-57a3e0":    (10, 11),
    "TOP-LOGARIFMICHESKIE-FUNKTSII-aa40ea":    (10, 11),

    # ── Тригонометрия ───────────────────────────────────────────────────
    "TOP-EDINICHNAYA-OKRUZHNOST-7311af":       (9, 10),
    "TOP-RADIANNAYA-MERA-51263f":              (9, 10),
    "TOP-TRIGONOMETRICHESKIE-FUNKTSII-84c00c": (10, 11),
    "TOP-TRIGONOMETRICHESKIE-TOZHDESTVA-b4326d": (10, 11),
    "TOP-TRIGONOMETRICHESKIE-URAVNENIYA-37c238": (10, 11),
    "TOP-TRIGONOMETRICHESKIE-NERAVENSTV-a65a77": (10, 11),

    # ── Геометрия ───────────────────────────────────────────────────────
    "TOP-GEOMETRICHESKIE-FIGURY-001":          (5, 6),
    "TOP-PERIMETR-I-PLOSHCHAD-003":            (5, 6),
    "TOP-TOCHKA-I-PRYAMAYA-291b4a":            (7, 7),
    "TOP-UGLY-9cbfc3":                         (7, 7),
    "TOP-TREUGOLNIKI-de676b":                  (7, 9),
    "TOP-OKRUZHNOST-926fe8":                   (7, 9),
    "TOP-PLOSCHADI-c811e2":                    (8, 9),
    "TOP-PODOBIE-86fb4a":                      (8, 9),
    "TOP-MNOGOGRANNIKI-dd928d":                (10, 11),
    "TOP-PRYAMAYA-I-PLOSKOST-1d0194":          (10, 11),
    "TOP-TELA-VRASCHENIYA-722214":             (10, 11),
    "TOP-OBYOMY-d44ad9":                       (10, 11),

    # ── Аналитическая геометрия ─────────────────────────────────────────
    "TOP-VEKTORY-78d40c":                      (9, 11),
    "TOP-DEKARTOVY-KOORDINATY-19b067":         (9, 9),
    "TOP-SKALYARNOE-PROIZVEDENIE-5c6f65":      (9, 11),
    "TOP-URAVNENIE-PRYAMOJ-f56905":           (9, 11),
    "TOP-URAVNENIE-OKRUZHNOSTI-9f8fcf":       (9, 11),
    "TOP-KRIVYE-VTOROGO-PORYADKA-6f671e":      (10, 11),
    "TOP-PLOSKOST-V-PROSTRANSTVE-f03ae1":      (10, 11),

    # ── Математический анализ ───────────────────────────────────────────
    "TOP-PREDEL-POSLEDOVATELNOSTI-248f64":     (10, 11),
    "TOP-PREDEL-FUNKTSII-1925e2":              (10, 11),
    "TOP-PROIZVODNAYA-cfd26d":                 (10, 11),
    "TOP-PRAVILA-DIFFERENTSIROVANIYA-3bd912":  (10, 11),
    "TOP-ISSLEDOVANIE-FUNKTSIJ-726a8f":        (10, 11),
    "TOP-PERVOOBRAZNAYA-e23096":               (10, 11),
    "TOP-OPREDELYONNYJ-INTEGRAL-2f73d5":       (10, 11),
    "TOP-PRIMENENIYA-INTEGRALA-d4e675":        (10, 11),

    # ── Математические основания ────────────────────────────────────────
    "TOP-PONYATIE-MNOZHESTVA-124deb":          (7, 8),
    "TOP-OPERATSII-NAD-MNOZHESTVAMI-0c2eef":  (7, 8),
    "TOP-VYSKAZYVANIYA-efcd74":                (7, 8),
    "TOP-LOGICHESKIE-SVYAZKI-9db1f9":          (8, 9),
    "TOP-LOGICHESKIE-ZAKONY-3b4f49":           (8, 9),
    "TOP-KVANTORY-830065":                     (10, 11),
    "TOP-METODY-DOKAZATELSTVA-c72a13":         (10, 11),
    "TOP-OTNOSHENIYA-142ca8":                  (10, 11),
    "TOP-OTOBRAZHENIYA-eb11ba":                (10, 11),
    "TOP-EKVIVALENTNOST-I-PORYADOK-a24b0a":    (10, 11),

    # ── Линейная алгебра ────────────────────────────────────────────────
    "TOP-MATRITSY-c1cc7f":                     (10, 11),
    "TOP-OPREDELITELI-3723cc":                 (10, 11),
    "TOP-OBRATNAYA-MATRITSA-c589a4":           (10, 11),
    "TOP-LINEJNAYA-KOMBINATSIYA-31422b":       (10, 11),
    "TOP-BAZIS-9efbe8":                        (10, 11),
    "TOP-RAZMERNOST-cb7976":                   (10, 11),

    # ── Дискретная математика ───────────────────────────────────────────
    "TOP-GRAFY-21142f":                        (8, 9),
    "TOP-DEREVYA-6faba1":                      (8, 9),
    "TOP-PUTI-I-TSIKLY-17a10d":                (9, 11),
    "TOP-TABLITSY-ISTINNOSTI-e872d3":          (8, 9),
    "TOP-BULEVY-FUNKTSII-30a3b0":              (9, 11),
    "TOP-ZAKONY-BULEVOJ-ALGEBRY-893ed4":       (9, 11),

    # ── Комбинаторика и вероятность ─────────────────────────────────────
    "TOP-OPREDELENIE-VEROYATNOSTI-f1aab2":     (5, 7),
    "TOP-SOBYTIYA-I-IH-KLASSIFIKA-97f448":     (5, 7),
    "TOP-OSNOVY-TEORII-VEROYATNOS-c8e176":     (7, 9),
    "TOP-SLUCHAJNYE-SOBYTIYA-f288f9":          (7, 9),
    "TOP-SVOISTVA-VEROYATNOSTI-51b7ce":        (7, 9),
    "TOP-NEZAVISIMYE-SOBYTIYA-bdea5e":         (8, 9),
    "TOP-USLOVNAYA-VEROYATNOST-8ea76c":        (9, 11),
    "TOP-FORMULA-BAJESA-9e1a3f":               (10, 11),
    "TOP-PRAVILA-PODSCHYOTA-db0161":           (5, 7),
    "TOP-PERESTANOVKI-469134":                 (9, 11),
    "TOP-RAZMESCHENIYA-382d73":                (9, 11),
    "TOP-SOCHETANIYA-01b667":                  (9, 11),
    "TOP-KOMBINATORIKA-V-VEROYATN-88900f":     (9, 11),
    "TOP-VEROYATNOST-d3cd07":                  (7, 9),
    "TOP-SLUCHAINYE-VELICHINY-90d9e2":         (10, 11),
    "TOP-MATEMATICHESKOE-OZHIDANI-d5d8c8":     (10, 11),
    "TOP-DISPERSIYA-I-STANDARTNOE-15d0f1":     (10, 11),
    "TOP-RASPREDELENIE-VEROYATNOS-4c5863":     (10, 11),
    "TOP-VVEDENIE-V-VEROYATNOSTNY-e344b3":     (10, 11),
    "TOP-RASPREDELENIE-BERNULLI-I-2654ca":     (10, 11),
    "TOP-RASPREDELENIE-PUASSONA-66bdaa":       (10, 11),
    "TOP-DISKRETNYE-VEROYATNOSTNY-450411":     (10, 11),
    "TOP-NEPRERYVNYE-VEROYATNOSTN-236631":     (10, 11),
    "TOP-NORMALNOE-RASPREDELENIE-ce0938":      (10, 11),
    "TOP-EKSPONENCIALNOE-RASPREDE-a30410":     (10, 11),
    "TOP-PRIMENENIE-VEROYATNOSTNY-3216ba":     (10, 11),
    "TOP-CENTRALNAYA-PREDELNAYA-T-b48f16":     (10, 11),
    "TOP-ZAKON-BOLSHIH-CHISEL-efc36b":         (10, 11),
    "TOP-MODELIROVANIE-SLUCHAINYH-ddc404":     (10, 11),

    # ── Статистика (секционные) ─────────────────────────────────────────
    "TOP-MERY-CENTRALNOI-TENDENCI-75dcdc":     (7, 9),
    "TOP-MERY-RAZBROSA-c487ac":                (7, 9),
    "TOP-SREDNIE-HARAKTERISTIKI-b231f6":       (7, 9),
    "TOP-RAZBROS-ac7a78":                      (7, 9),
    "TOP-KOEFFICIENTY-ASIMMETRII--55d6ee":     (10, 11),

    # ── Статистика (без секции) ─────────────────────────────────────────
    "TOP-OSNOVNYE-PONYATIYA-STATI-2d24ef":     (7, 9),
    "TOP-TIPY-DANNYH-I-UROVNI-IZM-c9a86a":    (7, 9),
    "TOP-SBOR-DANNYH-METODY-I-INS-60afe1":    (7, 9),
    "TOP-OPISANIE-DANNYH-MERY-CEN-4cff59":    (7, 9),
    "TOP-OPISANIE-DANNYH-MERY-RAZ-65807e":    (7, 9),
    "TOP-GRAFICHESKOE-PREDSTAVLEN-c2da9b":     (7, 9),
    "TOP-VIZUALIZACIYA-DANNYH-GRA-d211d6":     (7, 9),
    "TOP-SVODNYE-TABLICY-c6cff5":              (8, 11),
    "TOP-VYBORKA-3370b5":                      (10, 11),
    "TOP-VYBORKA-I-POPULYACIYA-471a66":        (10, 11),
    "TOP-OSHIBKI-VYBORKI-024504":              (10, 11),
    "TOP-INTERPRETACIYA-STATISTIC-460db0":     (9, 11),
    "TOP-PRIMENENIE-STATISTIKI-V--dcd30e":     (9, 11),
    "TOP-RABOTA-S-DANNYMI-005":                (7, 9),
    "TOP-VVEDENIE-V-OPISATELNUYU--a52049":     (7, 9),
    "TOP-KORRELYACIONNYI-ANALIZ-d5a590":       (10, 11),
    "TOP-KORRELYACIYA-I-REGRESSIY-43dd38":     (10, 11),
    "TOP-KORRELYATSIYA-7d5d50":                (10, 11),
    "TOP-PROVERKA-GIPOTEZ-9511b6":             (10, 11),
    "TOP-TESTIROVANIE-GIPOTEZ-S-I-83526e":     (10, 11),
    "TOP-OCENKA-PARAMETROV-RASPRE-f0b295":     (10, 11),

    # ── ОГЭ-specific ────────────────────────────────────────────────────
    "TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026":          (9, 9),
    "TOP-OGE-GEOMETRICHESKOE-DOKAZATELSTVO-2026":       (9, 9),
    "TOP-OGE-PRAKTIKO-ORIENTIROVANNYE-ZADACHI-2026":    (9, 9),

    # ── ЕГЭ-specific ────────────────────────────────────────────────────
    "TOP-EGE-EKONOMICHESKIE-ZADACHI-2026":     (11, 11),
    "TOP-EGE-FINANSOVAYA-MATEMATIKA-2026":     (11, 11),
    "TOP-EGE-PLANIMETRIYA-ZADACHI-2026":       (11, 11),
    "TOP-EGE-STEREOMETRIYA-ZADACHI-2026":      (11, 11),
    "TOP-EGE-TEORIYA-CHISEL-DELIMOST-2026":    (11, 11),
    "TOP-EGE-ZADACHI-S-PARAMETROM-2026":       (11, 11),

    # ── 25 canonical TOP-MATH-* ─────────────────────────────────────────
    "TOP-MATH-EQUATIONS-SYSTEMS":              (9, 11),
    "TOP-MATH-PLANE-GEOMETRY":                 (9, 11),
    "TOP-MATH-FUNCTIONS-GRAPHS":               (9, 11),
    "TOP-MATH-PROBABILITY-STATISTICS":         (9, 11),
    "TOP-MATH-APPLIED-MATH":                   (9, 11),
    "TOP-MATH-ALGEBRA-TRANSFORMS":             (9, 9),
    "TOP-MATH-INEQUALITIES":                   (9, 9),
    "TOP-MATH-PROGRESSIONS":                   (9, 9),
    "TOP-MATH-ADVANCED-ALGEBRA":               (9, 9),
    "TOP-MATH-ADVANCED-PLANE-GEOM":            (9, 9),
    "TOP-MATH-ADVANCED-FUNCTIONS":             (9, 9),
    "TOP-MATH-NUMBERS-CALCULATIONS":           (11, 11),
    "TOP-MATH-DERIVATIVES":                    (11, 11),
    "TOP-MATH-STEREOMETRY":                    (11, 11),
    "TOP-MATH-TRIGONOMETRY":                   (11, 11),
    "TOP-MATH-EXP-LOG":                        (11, 11),
    "TOP-MATH-CALCULUS":                       (11, 11),
    "TOP-MATH-ADVANCED-TRIG":                  (11, 11),
    "TOP-MATH-STEREOMETRY-ADVANCED":           (11, 11),
    "TOP-MATH-FINANCIAL-ADVANCED":             (11, 11),
    "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF":      (11, 11),
    "TOP-MATH-OPTIMIZATION":                   (11, 11),
    "TOP-MATH-NUMBER-THEORY":                  (11, 11),
    "TOP-MATH-COMPLEX-INEQUALITIES":           (11, 11),
    "TOP-MATH-COMBINATORICS":                  (11, 11),
}


def migrate(dry_run: bool = False) -> None:
    repo = Neo4jRepo()
    drv = repo.driver

    methods_updated = 0
    examples_updated = 0
    topics_processed = 0
    topics_missing = 0

    try:
        with drv.session() as session:
            # ── Step 1: SET user_class_min/max on Methods via Topic→Skill→Method ─
            print("=" * 60)
            print("Step 1: Update Method nodes with grade ranges")
            print("=" * 60)

            for topic_uid, (uc_min, uc_max) in sorted(TOPIC_GRADES.items()):
                # Check topic exists
                check = session.run(
                    "MATCH (t:Topic {uid: $uid, tenant_id: $tid}) RETURN t.title AS title",
                    uid=topic_uid, tid=TENANT_ID,
                ).single()
                if not check:
                    print(f"  [SKIP] Topic not found: {topic_uid}")
                    topics_missing += 1
                    continue

                title = check["title"]
                topics_processed += 1

                if not dry_run:
                    # Update methods: only set if currently NULL (don't overwrite
                    # grade-specific methods created by seed_methods_by_grade.py).
                    result = session.run(
                        """
                        MATCH (t:Topic {uid: $uid, tenant_id: $tid})
                              -[:REQUIRES_SKILL]->(sk:Skill)
                              -[:HAS_METHOD]->(m:Method)
                        WHERE m.user_class_min IS NULL
                        SET m.user_class_min = $uc_min,
                            m.user_class_max = $uc_max
                        RETURN count(m) AS cnt
                        """,
                        uid=topic_uid, tid=TENANT_ID,
                        uc_min=uc_min, uc_max=uc_max,
                    ).single()
                    n = result["cnt"] if result else 0

                    # Also update examples reachable via Method→HAS_EXAMPLE
                    ex_result = session.run(
                        """
                        MATCH (t:Topic {uid: $uid, tenant_id: $tid})
                              -[:REQUIRES_SKILL]->(sk:Skill)
                              -[:HAS_METHOD]->(m:Method)
                              -[:HAS_EXAMPLE]->(ex:Example)
                        WHERE ex.user_class_min IS NULL
                        SET ex.user_class_min = $uc_min,
                            ex.user_class_max = $uc_max
                        RETURN count(ex) AS cnt
                        """,
                        uid=topic_uid, tid=TENANT_ID,
                        uc_min=uc_min, uc_max=uc_max,
                    ).single()
                    n_ex = ex_result["cnt"] if ex_result else 0
                else:
                    # Dry-run: count what would be updated
                    result = session.run(
                        """
                        MATCH (t:Topic {uid: $uid, tenant_id: $tid})
                              -[:REQUIRES_SKILL]->(sk:Skill)
                              -[:HAS_METHOD]->(m:Method)
                        WHERE m.user_class_min IS NULL
                        RETURN count(m) AS cnt
                        """,
                        uid=topic_uid, tid=TENANT_ID,
                    ).single()
                    n = result["cnt"] if result else 0

                    ex_result = session.run(
                        """
                        MATCH (t:Topic {uid: $uid, tenant_id: $tid})
                              -[:REQUIRES_SKILL]->(sk:Skill)
                              -[:HAS_METHOD]->(m:Method)
                              -[:HAS_EXAMPLE]->(ex:Example)
                        WHERE ex.user_class_min IS NULL
                        RETURN count(ex) AS cnt
                        """,
                        uid=topic_uid, tid=TENANT_ID,
                    ).single()
                    n_ex = ex_result["cnt"] if ex_result else 0

                methods_updated += n
                examples_updated += n_ex
                if n or n_ex:
                    mode = "DRY" if dry_run else "SET"
                    print(f"  [{mode}] {topic_uid:<55s} {uc_min:>2d}-{uc_max:<2d}  {n:>2d} methods, {n_ex:>2d} examples  | {title}")

            # ── Step 2: Also update Topic nodes themselves ───────────────
            print()
            print("=" * 60)
            print("Step 2: Update Topic nodes with grade ranges")
            print("=" * 60)
            topics_with_grades = 0
            for topic_uid, (uc_min, uc_max) in sorted(TOPIC_GRADES.items()):
                if not dry_run:
                    result = session.run(
                        """
                        MATCH (t:Topic {uid: $uid, tenant_id: $tid})
                        WHERE t.user_class_min IS NULL
                        SET t.user_class_min = $uc_min,
                            t.user_class_max = $uc_max
                        RETURN count(t) AS cnt
                        """,
                        uid=topic_uid, tid=TENANT_ID,
                        uc_min=uc_min, uc_max=uc_max,
                    ).single()
                    n = result["cnt"] if result else 0
                else:
                    result = session.run(
                        "MATCH (t:Topic {uid: $uid, tenant_id: $tid}) WHERE t.user_class_min IS NULL RETURN count(t) AS cnt",
                        uid=topic_uid, tid=TENANT_ID,
                    ).single()
                    n = result["cnt"] if result else 0
                topics_with_grades += n

            print(f"  {'[DRY]' if dry_run else '[SET]'} Updated {topics_with_grades} Topic nodes")

    finally:
        repo.close()

    # ── Summary ──────────────────────────────────────────────────────────
    mode = "(DRY RUN)" if dry_run else "(APPLIED)"
    print()
    print("=" * 60)
    print(f"Migration complete {mode}")
    print(f"  Topics processed:    {topics_processed}")
    print(f"  Topics missing:      {topics_missing}")
    print(f"  Methods updated:     {methods_updated}")
    print(f"  Examples updated:    {examples_updated}")
    print(f"  Topics with grades:  {topics_with_grades}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    print("Migrate: SET user_class_min/max on all Method + Example nodes")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'WRITE'}")
    print(f"Total topics in mapping: {len(TOPIC_GRADES)}")
    print()
    migrate(dry_run=args.dry_run)
