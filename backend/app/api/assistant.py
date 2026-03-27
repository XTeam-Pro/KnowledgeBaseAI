from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from app.services.graph.neo4j_repo import relation_context, neighbors
from app.services.roadmap_planner import plan_route
from app.api.analytics import stats as analytics_stats
from app.services.questions import select_examples_for_topics, all_topic_uids_from_examples
from app.api.common import ApiError
from app.events.publisher import get_redis
from app.events.telemetry import track_event
from app.services.kb.builder import openai_chat_async
from app.config.settings import settings

router = APIRouter(prefix="/v1/assistant", tags=["ИИ ассистент"])


def _request_scope(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _enforce_rate_limit(request: Request, *, route_key: str, limit: int, window_sec: int = 60) -> None:
    try:
        r = get_redis()
        key = f"rl:{route_key}:{_request_scope(request)}"
        current = int(r.incr(key))
        if current == 1:
            r.expire(key, window_sec)
        if current > limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded, please try again later.")
    except HTTPException:
        raise
    except Exception:
        return

class ToolInfo(BaseModel):
    name: str
    description: str

class ToolsResponse(BaseModel):
    tools: List[ToolInfo]

@router.get(
    "/tools",
    summary="Список инструментов ассистента",
    description="Возвращает перечень доступных возможностей ИИ-ассистента.",
    response_model=ToolsResponse,
)
async def tools() -> Dict:
    """
    Принимает:
      - нет входных параметров

    Возвращает:
      - tools: список объектов {name, description} доступных действий ассистента
    """
    return {
        "tools": [
            {"name": "explain_relation", "description": "Объяснить связь между двумя узлами"},
            {"name": "viewport", "description": "Загрузить окрестность узла"},
            {"name": "roadmap", "description": "Построить учебный план"},
            {"name": "analytics", "description": "Показать метрики графа"},
            {"name": "questions", "description": "Сгенерировать адаптивные вопросы"},
        ]
    }

class AssistantChatInput(BaseModel):
    action: Optional[Literal["explain_relation", "viewport", "roadmap", "analytics", "questions"]] = Field(None, description="Explicit action to trigger. If None, treats as general chat.")
    message: str = Field(..., description="User message text.")
    from_uid: Optional[str] = Field(None, description="Context: source node.")
    to_uid: Optional[str] = Field(None, description="Context: target node.")
    center_uid: Optional[str] = Field(None, description="Context: center node for viewport.")
    depth: int = 1
    subject_uid: Optional[str] = None
    progress: Dict[str, float] = {}
    limit: int = 30
    count: int = 10
    difficulty_min: int = 1
    difficulty_max: int = 5
    exclude: List[str] = []

@router.post(
    "/chat",
    summary="Чат с ИИ-ассистентом",
    description="Единая точка для ИИ-ассистента. Поддерживает общий диалог или выполнение действий (дорожная карта, аналитика и т.д.) через поле `action`.",
    responses={
        400: {"model": ApiError, "description": "Некорректные параметры запроса"},
        502: {"model": ApiError, "description": "Ошибка запроса к LLM"},
        503: {"model": ApiError, "description": "Сервис LLM недоступен"},
    }
)
async def chat(payload: AssistantChatInput, request: Request) -> Dict:
    _enforce_rate_limit(request, route_key="assistant_chat", limit=35, window_sec=60)
    """
    Принимает:
      - action: одно из [explain_relation, viewport, roadmap, analytics, questions] или None для свободного ответа
      - message: текст вопроса
      - context-поля: from_uid/to_uid/center_uid/depth/subject_uid/progress и параметры генерации

    Возвращает:
      - В зависимости от action:
        - explain_relation: {answer, usage, context}
        - viewport: {nodes, edges, center_uid, depth}
        - roadmap: {items}
        - analytics: метрики графа
        - questions: {questions}
      - Свободный ответ: {answer, usage}
    """
    if payload.action == "explain_relation":
        if not payload.from_uid or not payload.to_uid:
            raise HTTPException(status_code=400, detail="from_uid/to_uid required")
        ctx = relation_context(payload.from_uid, payload.to_uid)
        messages = [
            {"role": "system", "content": "Ты эксперт по графу. Объясни, почему существует связь, используя метаданные."},
            {
                "role": "user",
                "content": f"Вопрос: {payload.message}\nОт: {ctx.get('from_title','')} ({payload.from_uid})\nК: {ctx.get('to_title','')} ({payload.to_uid})\nСвязь: {ctx.get('rel','')}\nСвойства: {ctx.get('props',{})}",
            },
        ]
        res = await openai_chat_async(
            messages,
            temperature=0.2,
            model=settings.fast_model,
            feature="assistant_explain_relation",
            max_tokens=350,
        )
        if not res.get("ok"):
            raise HTTPException(status_code=502, detail="LLM request failed")
        return {"answer": res.get("content", ""), "usage": res.get("usage"), "context": ctx}

    if payload.action == "viewport":
        if not payload.center_uid:
            raise HTTPException(status_code=400, detail="center_uid required")
        ns, es = neighbors(payload.center_uid, depth=payload.depth)
        return {"nodes": ns, "edges": es, "center_uid": payload.center_uid, "depth": payload.depth}

    if payload.action == "roadmap":
        items = plan_route(payload.subject_uid, payload.progress, limit=payload.limit)
        return {"items": items}

    if payload.action == "analytics":
        return await analytics_stats()

    if payload.action == "questions":
        roadmap = plan_route(payload.subject_uid, payload.progress, limit=payload.count * 3)
        topic_uids = [it["uid"] for it in roadmap] or all_topic_uids_from_examples()
        examples = select_examples_for_topics(
            topic_uids=topic_uids,
            limit=payload.count,
            difficulty_min=payload.difficulty_min,
            difficulty_max=payload.difficulty_max,
            exclude_uids=set(payload.exclude),
        )
        return {"questions": examples}

    messages = [
        {"role": "system", "content": "Ты ассистент платформы KnowledgeBase: помогаешь с графом, планом обучения и вопросами."},
        {"role": "user", "content": payload.message},
    ]
    res = await openai_chat_async(
        messages,
        temperature=0.2,
        model=settings.fast_model,
        feature="assistant_free_chat",
        max_tokens=350,
    )
    if not res.get("ok"):
        raise HTTPException(status_code=502, detail="LLM request failed")
    try:
        track_event("kb_assistant_chat", {"action": payload.action or "free_chat"})
    except Exception:
        pass
    return {"answer": res.get("content", ""), "usage": res.get("usage")}
