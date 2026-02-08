import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

from neo4j_utils import (
    update_dynamic_weight,
    update_skill_dynamic_weight,
    get_current_knowledge_level,
    get_current_skill_level,
    build_adaptive_roadmap,
    get_driver,
    ensure_weight_defaults,
    recompute_relationship_weights,
    update_user_topic_weight,
    update_user_skill_weight,
    get_user_topic_level,
    get_user_skill_level,
    build_user_roadmap,
    add_prereq_safe,
    add_topic_skill,
    link_skill_method,
    validate_prereq_global,
    complete_user_topic,
    complete_user_skill,
)
from s3_utils import presign_put, presign_get
from qdrant_utils import upsert_point as qdrant_upsert_point, search as qdrant_search
from embedding_utils import generate_embedding
import psycopg2

app = FastAPI(
    title="KnowledgeBaseAI API",
    description=(
        "Единая база знаний (Neo4j) с персонализацией."
        "\nГлобальные статичные веса и динамичные веса; пользовательские веса не изменяют первичные данные."
        "\nЭндпоинты поддерживают глобальные и персональные сценарии обучения."
    ),
    version="1.0.0",
)


class TestResult(BaseModel):
    topic_uid: str
    score: float
    user_id: str | None = None


class SkillTestResult(BaseModel):
    skill_uid: str
    score: float
    user_id: str | None = None


class RoadmapRequest(BaseModel):
    subject_uid: str | None = None
    limit: int = 50


@app.get("/health", summary="Health check", description="Check if the API is running")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "KnowledgeBaseAI"}


@app.on_event("startup")
def startup_event():
    driver = get_driver()
    with driver.session() as session:
        ensure_weight_defaults(session)
    driver.close()


def require_api_key(x_api_key: str | None) -> None:
    import os
    expected = os.getenv('ADMIN_API_KEY')
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid api key")


def get_db_config() -> Dict:
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'knowledge_base'),
        'user': os.getenv('DB_USER', 'kb_user'),
        'password': os.getenv('DB_PASSWORD', 'kb_password'),
        'port': int(os.getenv('DB_PORT', '5432')),
    }


def db_connect():
    return psycopg2.connect(**get_db_config())


@app.post("/test_result", summary="Обновить результат теста темы", description=(
    "Обновляет динамичный вес темы."
    "\nЕсли передан user_id — обновляет пользовательскую связь User-[:PROGRESS_TOPIC]->Topic;"
    " иначе — глобальный dynamic_weight темы."
    "\nПосле обновления пересчитывает adaptive_weight на связях Skill-[:LINKED]->Method."
))
def submit_test_result(payload: TestResult) -> Dict:
    try:
        if payload.user_id:
            updated = update_user_topic_weight(payload.user_id, payload.topic_uid, payload.score)
        else:
            updated = update_dynamic_weight(payload.topic_uid, payload.score)
        stats = recompute_relationship_weights()
        return {"ok": True, "updated": updated, "recomputed": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/skill_test_result", summary="Обновить результат теста навыка", description=(
    "Обновляет динамичный вес навыка."
    "\nЕсли передан user_id — обновляет пользовательскую связь User-[:PROGRESS_SKILL]->Skill;"
    " иначе — глобальный dynamic_weight навыка."
    "\nПосле обновления пересчитывает adaptive_weight на связях Skill-[:LINKED]->Method."
))
def submit_skill_test_result(payload: SkillTestResult) -> Dict:
    try:
        if payload.user_id:
            updated = update_user_skill_weight(payload.user_id, payload.skill_uid, payload.score)
        else:
            updated = update_skill_dynamic_weight(payload.skill_uid, payload.score)
        stats = recompute_relationship_weights()
        return {"ok": True, "updated": updated, "recomputed": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/knowledge_level/{topic_uid}", summary="Уровень знаний по теме (глобально)", description=(
    "Возвращает статичный и динамичный вес темы в глобальном графе."
    "\nИспользуется для агрегированного обзора без персонализации."
))
def get_knowledge_level(topic_uid: str) -> Dict:
    try:
        lvl = get_current_knowledge_level(topic_uid)
        return {"ok": True, "level": lvl}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/skill_level/{skill_uid}", summary="Уровень по навыку (глобально)", description=(
    "Возвращает статичный и динамичный вес навыка в глобальном графе."
    "\nИспользуется для агрегированного обзора без персонализации."
))
def get_skill_level(skill_uid: str) -> Dict:
    try:
        lvl = get_current_skill_level(skill_uid)
        return {"ok": True, "level": lvl}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/roadmap", summary="Глобальная дорожная карта обучения", description=(
    "Строит список тем, навыков и методов, отсортированный по глобальному dynamic_weight темы."
    "\nПараметры: subject_uid (опционально ограничивает предмет), limit (ограничение размера)."
))
def get_roadmap(payload: RoadmapRequest) -> Dict:
    try:
        items = build_adaptive_roadmap(payload.subject_uid, payload.limit)
        return {"ok": True, "roadmap": items}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/user/knowledge_level/{user_id}/{topic_uid}", summary="Уровень пользователя по теме", description=(
    "Возвращает статичный вес темы и персональный dynamic_weight пользователя по теме"
    " (если нет пользовательской записи, используется глобальный dynamic_weight/статичный вес)."
))
def get_user_knowledge_level(user_id: str, topic_uid: str) -> Dict:
    try:
        lvl = get_user_topic_level(user_id, topic_uid)
        return {"ok": True, "level": lvl}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/user/skill_level/{user_id}/{skill_uid}", summary="Уровень пользователя по навыку", description=(
    "Возвращает статичный вес навыка и персональный dynamic_weight пользователя по навыку"
    " (если нет пользовательской записи, используется глобальный dynamic_weight/статичный вес)."
))
def get_user_skill_level(user_id: str, skill_uid: str) -> Dict:
    try:
        lvl = get_user_skill_level(user_id, skill_uid)
        return {"ok": True, "level": lvl}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


class UserRoadmapRequest(BaseModel):
    user_id: str
    subject_uid: str | None = None
    limit: int = 50
    penalty_factor: float | None = 0.15


@app.post("/user/roadmap", summary="Персональная дорожная карта обучения", description=(
    "Строит дорожную карту для пользователя: темы сортируются по персональному dynamic_weight."
    "\nВозвращает темы с приоритетами, связанные навыки/методы с учетом пользовательских весов."
))
def get_user_roadmap(payload: UserRoadmapRequest) -> Dict:
    try:
        items = build_user_roadmap(payload.user_id, payload.subject_uid, payload.limit, payload.penalty_factor or 0.15)
        return {"ok": True, "roadmap": items}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class CompleteTopicRequest(BaseModel):
    user_id: str
    topic_uid: str
    time_spent_sec: float
    errors: int = 0


@app.post("/user/complete_topic", summary="Зафиксировать завершение темы", description=(
    "Создаёт связь User-[:COMPLETED]->Topic с метриками времени и ошибок."
))
def api_complete_topic(payload: CompleteTopicRequest) -> Dict:
    try:
        return complete_user_topic(payload.user_id, payload.topic_uid, payload.time_spent_sec, payload.errors)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class CompleteSkillRequest(BaseModel):
    user_id: str
    skill_uid: str
    time_spent_sec: float
    errors: int = 0


@app.post("/user/complete_skill", summary="Зафиксировать завершение навыка", description=(
    "Создаёт связь User-[:COMPLETED]->Skill с метриками времени и ошибок."
))
def api_complete_skill(payload: CompleteSkillRequest) -> Dict:
    try:
        return complete_user_skill(payload.user_id, payload.skill_uid, payload.time_spent_sec, payload.errors)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class AddPrereqRequest(BaseModel):
    topic_uid: str
    prereq_uid: str


@app.post("/graph/add_prereq", summary="Безопасно добавить PREREQ ребро", description=(
    "Создаёт ребро Topic-[:PREREQ]->Topic только если не образуется цикл (DAG-проверка)."
))
def api_add_prereq(payload: AddPrereqRequest, x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        res = add_prereq_safe(payload.topic_uid, payload.prereq_uid)
        if not res.get("ok"):
            raise HTTPException(status_code=400, detail=res.get("reason", "failed"))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class UseSkillRequest(BaseModel):
    topic_uid: str
    skill_uid: str


@app.post("/graph/use_skill", summary="Добавить связь Topic→USES_SKILL→Skill", description=(
    "Прямая связь темы с навыком для точного планирования и подбора методов."
))
def api_use_skill(payload: UseSkillRequest, x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        res = add_topic_skill(payload.topic_uid, payload.skill_uid)
        if not res.get("ok"):
            raise HTTPException(status_code=400, detail=res.get("reason", "failed"))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class LinkMethodRequest(BaseModel):
    skill_uid: str
    method_uid: str
    weight: str | None = None
    confidence: float | None = None


@app.post("/graph/link_method", summary="Связать Skill→LINKED→Method", description=(
    "Создаёт или обновляет связь навыка с методом с весом/уверенностью."
))
def api_link_method(payload: LinkMethodRequest, x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        res = link_skill_method(payload.skill_uid, payload.method_uid, payload.weight, payload.confidence)
        if not res.get("ok"):
            raise HTTPException(status_code=400, detail=res.get("reason", "failed"))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class PresignPutRequest(BaseModel):
    key: str
    expiry_sec: int | None = 600


@app.post("/media/presign_put", summary="Получить presigned URL для загрузки в S3", description=(
    "Возвращает временную ссылку PUT для загрузки объекта в S3 совместимое хранилище (MinIO)."
))
def api_media_presign_put(payload: PresignPutRequest, x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        return presign_put(payload.key, int(payload.expiry_sec or 600))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class PresignGetRequest(BaseModel):
    key: str
    expiry_sec: int | None = 600


@app.post("/media/presign_get", summary="Получить presigned URL для скачивания из S3", description=(
    "Возвращает временную ссылку GET для доступа к объекту в S3 совместимом хранилище (MinIO)."
))
def api_media_presign_get(payload: PresignGetRequest, x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        return presign_get(payload.key, int(payload.expiry_sec or 600))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class QdrantUpsertRequest(BaseModel):
    collection: str
    point_id: str
    text: str
    payload: Dict


@app.post("/qdrant/upsert", summary="Qdrant upsert точки", description=(
    "Создаёт/обновляет точку в коллекции Qdrant по идентификатору с вектором и payload."
))
def api_qdrant_upsert(payload: QdrantUpsertRequest, x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        vec = generate_embedding(payload.text)
        return qdrant_upsert_point(payload.collection, payload.point_id, vec, payload.payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class QdrantSearchRequest(BaseModel):
    collection: str
    vector: List[float]
    limit: int | None = 10
    filter_payload: Dict | None = None


@app.post("/qdrant/search", summary="Qdrant поиск по вектору", description=(
    "Ищет близкие объекты в коллекции Qdrant по вектору с необязательным фильтром по payload."
))
def api_qdrant_search(payload: QdrantSearchRequest) -> Dict:
    try:
        return qdrant_search(payload.collection, payload.vector, int(payload.limit or 10), payload.filter_payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/graph/validate_prereq", summary="Глобальная DAG‑валидация PREREQ", description=(
    "Проверяет весь граф тем на наличие циклов в связях PREREQ."
))
def api_validate_prereq(x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        res = validate_prereq_global()
        return {"ok": res.get("ok"), "cycles": res.get("cycles")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/recompute_links", summary="Пересчитать adaptive_weight на связях LINKED", description=(
    "Пересчитывает свойство adaptive_weight для всех связей Skill-[:LINKED]->Method"
    " на основе текущих динамичных весов навыков (глобально или после обновлений пользователя)."
))
def recompute_links(x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        stats = recompute_relationship_weights()
        return {"ok": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class CreateAttemptRequest(BaseModel):
    user_id: str
    example_uid: str
    source: str | None = None


@app.post("/oltp/attempts", summary="Создать попытку")
def create_attempt(payload: CreateAttemptRequest) -> Dict:
    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO attempts (user_id, example_uid, source, started_at) VALUES (%s, %s, %s, now()) RETURNING id",
                    (payload.user_id, payload.example_uid, payload.source)
                )
                rid = cur.fetchone()[0]
            conn.commit()
            return {"ok": True, "id": rid}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class AddStepRequest(BaseModel):
    step_order: int
    action: str


@app.post("/oltp/attempts/{attempt_id}/steps", summary="Добавить шаг")
def add_step(attempt_id: int, payload: AddStepRequest) -> Dict:
    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO steps (attempt_id, step_order, action, created_at) VALUES (%s, %s, %s, now())",
                    (attempt_id, payload.step_order, payload.action)
                )
            conn.commit()
            return {"ok": True}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class AddEvaluationRequest(BaseModel):
    skill_uid: str
    role: str
    accuracy: float
    critical: bool | None = False


@app.post("/oltp/attempts/{attempt_id}/evaluations", summary="Добавить оценку навыка")
def add_evaluation(attempt_id: int, payload: AddEvaluationRequest) -> Dict:
    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO evaluations (attempt_id, skill_uid, role, accuracy, critical, created_at) VALUES (%s, %s, %s, %s, %s, now())",
                    (attempt_id, payload.skill_uid, payload.role, payload.accuracy, bool(payload.critical))
                )
            conn.commit()
            return {"ok": True}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class AddErrorEventRequest(BaseModel):
    error_uid: str
    skill_uid: str | None = None
    example_uid: str | None = None
    critical: bool | None = False


@app.post("/oltp/attempts/{attempt_id}/errors", summary="Зафиксировать ошибку")
def add_error_event(attempt_id: int, payload: AddErrorEventRequest) -> Dict:
    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO error_events (attempt_id, error_uid, skill_uid, example_uid, critical, created_at) VALUES (%s, %s, %s, %s, %s, now())",
                    (attempt_id, payload.error_uid, payload.skill_uid, payload.example_uid, bool(payload.critical))
                )
            conn.commit()
            return {"ok": True}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class FinishAttemptRequest(BaseModel):
    time_spent_sec: int | None = None
    accuracy: float | None = None
    critical_errors_count: int | None = None


@app.post("/oltp/attempts/{attempt_id}/finish", summary="Завершить попытку")
def finish_attempt(attempt_id: int, payload: FinishAttemptRequest) -> Dict:
    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE attempts SET finished_at = now(), time_spent_sec = COALESCE(%s, time_spent_sec), accuracy = COALESCE(%s, accuracy), critical_errors_count = COALESCE(%s, critical_errors_count) WHERE id = %s",
                    (payload.time_spent_sec, payload.accuracy, payload.critical_errors_count, attempt_id)
                )
            conn.commit()
            return {"ok": True}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/oltp/apply_schema", summary="Применить схему PostgreSQL")
def apply_schema(x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        path = os.path.join(os.path.dirname(__file__), 'schemas', 'postgres.sql')
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="schema not found")
        with open(path, 'r', encoding='utf-8') as f:
            sql = f.read()
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            return {"ok": True}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class QdrantBulkIndexRequest(BaseModel):
    collection: str


def load_jsonl(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    items: List[Dict] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(__import__('json').loads(line))
            except Exception:
                continue
    return items


@app.post("/qdrant/index_bulk", summary="Bulk индексация в Qdrant")
def qdrant_index_bulk(payload: QdrantBulkIndexRequest, x_api_key: str | None = Header(default=None)) -> Dict:
    try:
        require_api_key(x_api_key)
        base = os.path.join(os.path.dirname(__file__), 'kb')
        col = payload.collection
        if col not in {"skills", "methods"}:
            raise HTTPException(status_code=400, detail="invalid collection")
        fname = 'skills.jsonl' if col == 'skills' else 'methods.jsonl'
        rows = load_jsonl(os.path.join(base, fname))
        cnt = 0
        for r in rows:
            uid = r.get('uid')
            title = r.get('title') or ''
            vec = generate_embedding(title)
            qdrant_upsert_point(col, uid, vec, r)
            cnt += 1
        return {"ok": True, "indexed": cnt}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
