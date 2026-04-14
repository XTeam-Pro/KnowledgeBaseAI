from typing import List, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from openai import AsyncOpenAI
from app.config.settings import settings

client = QdrantClient(url=str(settings.qdrant_url))
COLLECTION = "concepts"
try:
    if COLLECTION not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
except Exception:
    pass

# Configure OpenAI client based on LLM_PROVIDER setting
def _get_oai_client():
    provider = settings.llm_provider.lower()
    if provider == "openrouter":
        api_key = settings.open_router_api_key.get_secret_value() if settings.open_router_api_key else ""
        base_url = settings.openrouter_base_url
    else:
        api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else ""
        base_url = None
    return AsyncOpenAI(api_key=api_key, base_url=base_url, max_retries=0, timeout=20.0)

oai = _get_oai_client()
async def embed_text(text: str) -> List[float]:
    resp = await oai.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding
async def upsert_concept(uid: str, title: str, definition: str, embedding: List[float]) -> None:
    client.upsert(
        collection_name=COLLECTION,
        points=[PointStruct(id=uid, vector=embedding, payload={"title": title, "definition": definition})],
    )
def query_similar(embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
    res = client.search(collection_name=COLLECTION, query_vector=embedding, limit=top_k)
    return [(str(r.id), float(r.score)) for r in res]
