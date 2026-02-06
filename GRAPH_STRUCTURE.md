# KnowledgeBaseAI Graph Structure

## Overview
This document describes the DAG Invariant Graph structure after migration (Variant A).

**Date**: 2026-02-06
**Migration**: Completed successfully

---

## Core Principles

### 1. Invariant DAG (Directed Acyclic Graph)
- **Canonical Math Ontology** (CMO) is immutable
- **Curriculum Mappings** are projections (subset + order + priorities)
- **PREREQ relationships** represent strict logical dependencies
- **No cycles** allowed in either PREREQ or CONTAINS graphs

### 2. Two Relationship Types

#### PREREQ (Logical Dependencies)
Semantic: "A -[:PREREQ]-> B" means "A requires B as a prerequisite"
Translation: "To learn A, you must know B first"

**Current structure:**
- `Topic -[:PREREQ]-> Topic` (101 relationships)
- `Topic -[:PREREQ]-> Skill` (1,407 relationships)
- `Skill -[:PREREQ]-> Method` (2,323 relationships)
- **Total PREREQ**: 3,831 relationships

#### CONTAINS (Hierarchical Structure)
Semantic: "A -[:CONTAINS]-> B" means "A organizationally contains B"
Translation: "B is a structural part of A"

**Current structure:**
- `Subject -[:CONTAINS]-> Section` (13 relationships)
- `Section -[:CONTAINS]-> Subsection` (25 relationships)
- `Subsection -[:CONTAINS]-> Topic` (106 relationships)
- `Section -[:CONTAINS]-> Topic` (2 direct relationships)
- **Total CONTAINS**: 146 relationships

---

## Node Types

| Type | Count | Description |
|------|-------|-------------|
| **Subject** | 1 | Top-level subject (Mathematics) |
| **Section** | 13 | Major mathematical areas (Algebra, Geometry, etc.) |
| **Subsection** | 25 | Sub-areas within sections |
| **Topic** | 153 | Specific mathematical topics |
| **Skill** | 1,176 | Concrete skills/abilities |
| **Method** | 2,323 | Specific techniques/procedures |

**Total nodes**: 3,691

---

## Graph Properties

### ✅ Validated Invariants

1. **Acyclic PREREQ**: No cycles detected ✓
2. **Acyclic CONTAINS**: No cycles detected ✓
3. **Two relationship types only**: PREREQ + CONTAINS ✓
4. **DAG structure**: Confirmed ✓

### ⚠️ Known Issues

1. **Orphaned Topics**: 45 topics not connected to Subject via CONTAINS
   - Example: "Osnovy teorii veroyatnos", "Opredelenie veroyatnosti"
   - These topics exist in PREREQ graph but not in hierarchy
   - **Action required**: Add CONTAINS relationships to parent Subsections

2. **Orphaned Skill**: 1 skill without any relationships
   - "Конфликтное разрешение" (SKL-KONFLIKTNOE-RAZRESHENIE-31ab72)
   - **Action required**: Remove or connect to hierarchy

---

## Hierarchy Structure

```
Subject: Mathematics
├── Section: Математические основания
│   └── Subsection: ...
│       └── Topic: ...
├── Section: Алгебра
│   ├── Subsection: Уравнения
│   │   ├── Topic: Линейные уравнения
│   │   ├── Topic: Квадратные уравнения
│   │   └── ...
│   ├── Subsection: Неравенства
│   └── Subsection: Алгебраические выражения
├── Section: Геометрия
├── Section: Тригонометрия
└── ...
```

---

## Dependency Structure (PREREQ)

### Example: Topic Dependencies
```cypher
(Topic: "Таблицы истинности") -[:PREREQ]-> (Topic: "Логические связки")
(Topic: "Логические связки") -[:PREREQ]-> (Topic: "Высказывания")
```

### Example: Topic → Skill Dependencies
```cypher
(Topic: "Квадратные уравнения") -[:PREREQ]-> (Skill: "Определение квадратного уравнения")
(Topic: "Квадратные уравнения") -[:PREREQ]-> (Skill: "Методы решения квадратного уравнения")
(Topic: "Квадратные уравнения") -[:PREREQ]-> (Skill: "Формула корней квадратного уравнения")
```

### Example: Skill → Method Dependencies
```cypher
(Skill: "Сложение чисел") -[:PREREQ]-> (Method: "Сложение на числовом ряду")
(Skill: "Сложение чисел") -[:PREREQ]-> (Method: "Метод на пальцах")
```

---

## Migration History

### What Changed

| Action | Before | After |
|--------|--------|-------|
| **REQUIRES_SKILL → PREREQ** | 1,407 | Converted ✓ |
| **HAS_METHOD → PREREQ** | 2,323 | Converted ✓ |
| **HAS_SKILL** | 1,176 | Deleted (redundant) ✓ |
| **HAS_SECTION** | 12 | Deleted (duplicate) ✓ |
| **HAS_SUBSECTION** | 25 | Deleted (duplicate) ✓ |
| **HAS_TOPIC** | 106 | Deleted (duplicate) ✓ |
| **CONTAINS** | 146 | Retained ✓ |
| **PREREQ** | 101 → 3,831 | Expanded ✓ |

### Relationship Types
- **Before**: 8 types (PREREQ, REQUIRES_SKILL, HAS_METHOD, HAS_SKILL, HAS_SECTION, HAS_SUBSECTION, HAS_TOPIC, CONTAINS)
- **After**: 2 types (PREREQ, CONTAINS)

---

## Usage Patterns

### Query 1: Find all prerequisites for a topic
```cypher
MATCH path = (t:Topic {title: "Квадратные уравнения"})-[:PREREQ*]->(prereq)
RETURN path
```

### Query 2: Get topic hierarchy
```cypher
MATCH path = (subj:Subject)-[:CONTAINS*]->(t:Topic)
WHERE t.title = "Линейные уравнения"
RETURN path
```

### Query 3: Find all skills required for a topic
```cypher
MATCH (t:Topic {title: "Квадратные уравнения"})-[:PREREQ]->(sk:Skill)
RETURN sk.title as required_skill
```

### Query 4: Check for cycles (should return 0)
```cypher
MATCH path = (n)-[:PREREQ*]->(n)
RETURN count(path) as cycle_count
```

---

## Next Steps

1. **Fix orphaned topics**: Add CONTAINS relationships for 45 topics
2. **Remove orphaned skill**: Delete or connect "Конфликтное разрешение"
3. **Implement curriculum mappings**: Create projection layer on top of canonical graph
4. **Add curriculum entities**: Define Academic Core, School Core, STEM, Data Science, etc.
5. **Update API**: Modify endpoints to work with new PREREQ/CONTAINS structure

---

## Validation Scripts

See:
- [migration_to_dag.cypher](./migration_to_dag.cypher) - Migration script
- [validate_dag.cypher](./validate_dag.cypher) - Validation queries

---

## References

- Neo4j version: 5.26
- Graph database: KnowledgeBaseAI
- Tenant: default
