# Интеграция целевых Curricula в Roadmap Planner

## Резюме

Создана система **персонализированных учебных программ (curricula)** на основе целевых оценок/баллов студента. Теперь студент выбирает цель (например, "ОГЭ на 4" или "ЕГЭ Профиль 80+ баллов"), и roadmap автоматически включает только необходимые темы.

---

## Созданные Curricula

### ОГЭ 2026 (3 варианта)

| Code | Название | Целевая оценка | Задания | Темы | Ожидаемые баллы |
|------|----------|----------------|---------|------|-----------------|
| `RU-OGE-2026-G3` | ОГЭ 2026 Математика - На 3 | **3** | 1-16 | 25 | 8-14 баллов |
| `RU-OGE-2026-G4` | ОГЭ 2026 Математика - На 4 | **4** | 1-19 | 31 | 15-21 балл |
| `RU-OGE-2026-G5` | ОГЭ 2026 Математика - На 5 | **5** | 1-25 | 37 | 22-31 балл |

**Ключевое отличие:**
- **На 3:** Исключены задания части 2 (20-25) - не нужны для базовой оценки
- **На 4:** Исключена часть 2 (20-25) - достаточно части 1 для хорошей оценки
- **На 5:** Включены ВСЕ задания - необходимо решать повышенный уровень

### ЕГЭ База 2026 (3 варианта)

| Code | Название | Целевая оценка | Задания | Темы | Ожидаемые баллы |
|------|----------|----------------|---------|------|-----------------|
| `RU-EGE-BASE-2026-G3` | ЕГЭ База - На 3 | **3** | 1-11 | 42 | 7-11 баллов |
| `RU-EGE-BASE-2026-G4` | ЕГЭ База - На 4 | **4** | 1-16 | 59 | 12-16 баллов |
| `RU-EGE-BASE-2026-G5` | ЕГЭ База - На 5 | **5** | 1-21 | 76 | 17-21 балл |

**Ключевое отличие:**
- **На 3:** Минимум тем, акцент на практические задачи и базовую алгебру
- **На 4:** Исключена геометрия (задания 16-21) - можно сдать без нее
- **На 5:** Полная программа, включая стереометрию

### ЕГЭ Профиль 2026 (5 вариантов)

| Code | Название | Целевые баллы | Задания | Темы | Первичные баллы → Тестовые |
|------|----------|---------------|---------|------|----------------------------|
| `RU-EGE-PROF-2026-60` | ЕГЭ Профиль - 60+ | **60-69** | 1-12 | 17 | 12 → ~68 |
| `RU-EGE-PROF-2026-70` | ЕГЭ Профиль - 70+ | **70-79** | 1-13 | 19 | 14 → ~74 |
| `RU-EGE-PROF-2026-80` | ЕГЭ Профиль - 80+ | **80-89** | 1-16 | 21 | 18 → ~82 |
| `RU-EGE-PROF-2026-90` | ЕГЭ Профиль - 90+ | **90-94** | 1-17 | 21 | 23 → ~92 |
| `RU-EGE-PROF-2026-100` | ЕГЭ Профиль - 95-100 | **95-100** | 1-19 | 21 | 27+ → 96-100 |

**Ключевое отличие:**
- **60+:** Только часть 1 (базовые задания) - достаточно для поступления в большинство вузов
- **70+:** Часть 1 + легкое задание части 2 (уравнения или неравенства)
- **80+:** Часть 1 + половина части 2 (исключены параметры и олимпиадные задачи)
- **90+:** Почти вся программа, исключено только задание 19 (олимпиадное)
- **100:** Абсолютно ВСЕ темы, включая олимпиадную математику

---

## Архитектура решения

### Почему отдельные Curricula?

**Альтернативный подход** (от которого отказались):
- Хранить target_grade/target_score в профиле студента
- Фильтровать темы динамически при построении roadmap

**Выбранный подход** (через отдельные curricula):
✅ **Простота:** Логика фильтрации выполнена один раз при создании curriculum
✅ **Производительность:** Roadmap planner не делает сложных вычислений
✅ **Прозрачность:** Студент видит конкретный учебный план, а не абстрактную цель
✅ **Гибкость:** Можно вручную корректировать curriculum для конкретных случаев
✅ **Масштабируемость:** Легко добавить новые варианты (например, "ОГЭ для профильного класса")

### Как работает фильтрация

1. **Базовый curriculum** (например, `GEN-3045D621` - "Учебный план: Математика ОГЭ 2026")
   - Содержит ВСЕ темы с полями `exam_task_number`
   - Например: `exam_task_number = '15'` (геометрия), `'1-5'` (практические задачи)

2. **Целевой curriculum** (например, `RU-OGE-2026-G4` - "ОГЭ на 4")
   - SQL-функция `task_in_range(task_number, max_task)` проверяет, входит ли задание в диапазон
   - Копируются только темы, где `task_in_range(exam_task_number, 19) = true`
   - Исключаются темы с `exam_task_number IN ('20', '21', '22', '23-25')`

3. **Roadmap Planner**
   - Получает `curriculum_id` целевого curriculum
   - Извлекает `canonical_uid` тем из `curriculum_nodes`
   - Строит roadmap только по этим темам
   - **Результат:** Студент изучает ТОЛЬКО то, что нужно для его цели

---

## API Integration

### Текущий Roadmap Planner

Файл: `backend/app/services/roadmap_planner.py`

```python
def plan_route(subject_uid: str, progress: Dict[str, float], limit: int = 30) -> List[Dict]:
    # Текущая логика: строит roadmap по всем темам Subject
    # Не учитывает curriculum и целевые оценки
```

### Необходимые изменения

#### 1. Добавить параметр `curriculum_id` в функцию

```python
def plan_route(
    subject_uid: str | None,
    progress: Dict[str, float],
    curriculum_id: int | None = None,  # НОВОЕ
    limit: int = 30
) -> List[Dict]:
    """
    Строит адаптивный roadmap с учетом целевого curriculum.

    Если curriculum_id указан:
        - Извлекает темы из curriculum_nodes
        - Фильтрует граф только по этим темам
        - Roadmap содержит ТОЛЬКО необходимые темы

    Если curriculum_id = None:
        - Работает как раньше (все темы Subject)
    """
```

#### 2. Запрос тем для целевого curriculum

```python
if curriculum_id:
    # Получить список canonical_uid из curriculum_nodes
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT canonical_uid, order_index, exam_task_number
            FROM curriculum_nodes
            WHERE curriculum_id = %s
            ORDER BY order_index
        """, (curriculum_id,))
        curriculum_topics = [row[0] for row in cur.fetchall()]
    conn.close()

    # Фильтровать граф только по этим темам
    filtered_topics = [t for t in all_topics if t['uid'] in curriculum_topics]
else:
    # Без фильтрации (все темы Subject)
    filtered_topics = all_topics
```

#### 3. Обновить API endpoint

Файл: `backend/app/api/assistant.py`

```python
class AssistantChatInput(BaseModel):
    action: Optional[Literal["roadmap", ...]] = None
    subject_uid: Optional[str] = None
    curriculum_id: Optional[int] = None  # НОВОЕ
    progress: Dict[str, float] = {}
    limit: int = 30

@router.post("/chat")
async def chat(payload: AssistantChatInput) -> Dict:
    if payload.action == "roadmap":
        items = plan_route(
            subject_uid=payload.subject_uid,
            progress=payload.progress,
            curriculum_id=payload.curriculum_id,  # НОВОЕ
            limit=payload.limit
        )
        return {"items": items}
```

### Пример запроса от Frontend

```typescript
// Студент выбрал "ОГЭ на 4"
const response = await fetch('/v1/assistant/chat', {
  method: 'POST',
  body: JSON.stringify({
    action: 'roadmap',
    subject_uid: 'MATH-FULL-V1',
    curriculum_id: 13,  // RU-OGE-2026-G4
    progress: {
      'TOP-NATURALNYE-CHISLA-b27027': 0.8,
      'TOP-TEKSTOVYE-ZADACHI-004': 0.5
    },
    limit: 30
  })
});

// Roadmap будет содержать ТОЛЬКО темы из заданий 1-19
// Темы из заданий 20-25 (часть 2) НЕ попадут в roadmap
```

---

## Frontend Integration

### UI для выбора Curriculum

**Шаг 1: Экран выбора цели**

```tsx
<Select
  label="Выберите целевую оценку"
  options={[
    { value: 12, label: "ОГЭ 2026 - На 3 (базовый минимум)" },
    { value: 13, label: "ОГЭ 2026 - На 4 (хорошая оценка)" },
    { value: 14, label: "ОГЭ 2026 - На 5 (отличная оценка)" }
  ]}
  onChange={(curriculumId) => setSelectedCurriculum(curriculumId)}
/>
```

**Шаг 2: Отображение roadmap**

```tsx
// В компоненте Roadmap
const fetchRoadmap = async () => {
  const response = await api.post('/v1/assistant/chat', {
    action: 'roadmap',
    curriculum_id: selectedCurriculum, // из профиля студента
    progress: userProgress,
    limit: 30
  });

  setRoadmapItems(response.items);
};
```

**Шаг 3: Визуализация прогресса**

```tsx
<ProgressCard>
  <h3>ОГЭ 2026 - На 4</h3>
  <p>Нужно освоить задания 1-19 (31 тема)</p>
  <ProgressBar current={18} total={31} />
  <p>Осталось: 13 тем до оценки "4"</p>
</ProgressCard>
```

---

## Database Schema Updates (optional)

### Добавить поле в таблицу `users`

```sql
ALTER TABLE users
ADD COLUMN active_curriculum_id INTEGER REFERENCES curricula(id);

COMMENT ON COLUMN users.active_curriculum_id IS
'Активный curriculum студента (его целевая программа обучения)';
```

### Хранение истории целей

```sql
CREATE TABLE user_curriculum_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    curriculum_id INTEGER NOT NULL REFERENCES curricula(id),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    final_grade INTEGER,  -- Достигнутая оценка
    final_score INTEGER   -- Достигнутый балл (для ЕГЭ Профиль)
);

CREATE INDEX idx_user_curriculum_history_user ON user_curriculum_history(user_id);
```

---

## Roadmap Planner Logic Updates

### Фильтрация по curriculum_nodes

```python
def plan_route_with_curriculum(
    curriculum_id: int,
    progress: Dict[str, float],
    limit: int = 30
) -> List[Dict]:
    """
    Строит roadmap на основе curriculum_nodes.

    Алгоритм:
    1. Извлечь canonical_uid из curriculum_nodes для curriculum_id
    2. Построить dependency graph только для этих тем
    3. Ранжировать по сложности и зависимостям
    4. Вернуть топ-N тем с учетом progress
    """

    # 1. Получить темы curriculum
    curriculum_topics = get_curriculum_topics(curriculum_id)

    # 2. Построить граф зависимостей
    graph = build_dependency_graph(curriculum_topics)

    # 3. Фильтровать уже изученные (progress > 0.8)
    mastered = {uid for uid, score in progress.items() if score > 0.8}
    remaining_topics = [t for t in curriculum_topics if t not in mastered]

    # 4. Ранжировать по readiness (доступность = все prereq изучены)
    ranked_topics = rank_by_readiness(remaining_topics, mastered, graph)

    # 5. Вернуть top-N
    return ranked_topics[:limit]
```

### Пример output

```json
{
  "items": [
    {
      "uid": "TOP-NATURALNYE-CHISLA-b27027",
      "title": "Натуральные числа",
      "exam_task_number": "1-5",
      "mastery": 0.0,
      "readiness": 1.0,  // Нет prereq
      "estimated_hours": 2
    },
    {
      "uid": "TOP-LINEJNYE-URAVNENIYA-94fc09",
      "title": "Линейные уравнения",
      "exam_task_number": "9",
      "mastery": 0.3,
      "readiness": 0.8,  // 80% prereq освоено
      "estimated_hours": 3
    }
  ]
}
```

---

## Testing Scenarios

### Тест 1: Студент выбирает "ОГЭ на 3"

**Given:**
- Curriculum: `RU-OGE-2026-G3` (id=12)
- Progress: пустой (новый студент)

**Expected:**
- Roadmap содержит 25 тем
- Темы только из заданий 1-16
- НЕТ тем из заданий 20-25

**SQL для проверки:**
```sql
SELECT COUNT(*) FROM curriculum_nodes WHERE curriculum_id = 12;
-- Ожидается: 25
```

### Тест 2: Студент меняет цель с "на 3" на "на 4"

**Given:**
- Был curriculum: `RU-OGE-2026-G3`
- Новый curriculum: `RU-OGE-2026-G4`
- Progress: освоил 15 тем из части 1

**Expected:**
- Roadmap дополнительно включает темы заданий 17-19
- Уже освоенные темы НЕ показываются
- Roadmap содержит ~10-12 новых тем

### Тест 3: ЕГЭ Профиль 60+ vs 80+

**Given:**
- Curriculum A: `RU-EGE-PROF-2026-60` (17 тем, задания 1-12)
- Curriculum B: `RU-EGE-PROF-2026-80` (21 тема, задания 1-16)

**Expected:**
- Roadmap для 60+: НЕ содержит стереометрию (задание 14), параметры (18-19)
- Roadmap для 80+: содержит стереометрию и планиметрию повышенного уровня

---

## Next Steps

1. **Backend:**
   - [ ] Обновить `plan_route()` в `roadmap_planner.py`
   - [ ] Добавить `curriculum_id` в API `/v1/assistant/chat`
   - [ ] Добавить endpoint для списка доступных curricula: `GET /v1/curricula`
   - [ ] Тесты для фильтрации roadmap по curriculum

2. **Frontend:**
   - [ ] UI для выбора целевого curriculum
   - [ ] Сохранение `active_curriculum_id` в профиле студента
   - [ ] Отображение прогресса относительно целевого curriculum
   - [ ] Возможность сменить curriculum

3. **Database:**
   - [ ] (Опционально) Добавить `active_curriculum_id` в таблицу `users`
   - [ ] (Опционально) Создать `user_curriculum_history` для аналитики

4. **Analytics:**
   - [ ] Метрики: сколько студентов выбирают каждый curriculum
   - [ ] Конверсия: сколько достигают целевой оценки
   - [ ] A/B тест: эффективность персонализированных roadmap vs общих

---

## Sources

Все данные о баллах взяты из официальных источников:

- [Шкала перевода баллов ОГЭ 2026](https://ctege.info/oge-2026/shkala-perevoda-ballov-oge.html)
- [Баллы ОГЭ по математике](https://www.kp.ru/edu/shkola/bally-ogeh-po-matematike-v-9-klasse/)
- [Шкала ЕГЭ профиль](https://ctege.info/ege/ballyi-ege-po-matematike.html)
- [Шкала ЕГЭ база](https://vpr-ege.ru/ege/matematika-baza/2276-perevod-ballov-ege-po-matematike-baza-v-otsenki)
- [Демоверсии ФИПИ](https://fipi.ru/oge/demoversii-specifikacii-kodifikatory)
