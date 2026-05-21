import uuid
from typing import Dict, List
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from app.config.settings import settings
from app.services.graph.neo4j_repo import node_by_uid
from app.services.embeddings.provider import get_provider

ALLOWED_TYPES = {"Concept","Method","ContentUnit","Example"}
BATCH_SIZE = 64

def ensure_collection(client: QdrantClient, name: str, dim: int) -> None:
    cols = [c.name for c in client.get_collections().collections]
    if name not in cols:
        client.recreate_collection(collection_name=name, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))

def index_entities(tenant_id: str, uids: List[str], collection: str | None = None, dim: int | None = None) -> Dict:
    client = QdrantClient(url=str(settings.qdrant_url))
    name = collection or str(settings.qdrant_collection_name)
    d = int(dim or settings.qdrant_default_vector_dim)
    ensure_collection(client, name, d)
    prov = get_provider(dim_default=d)

    # Collect texts and metadata first, then embed in batches
    items: list[tuple[str, str, str]] = []  # (uid, typ, text)
    for uid in uids:
        props = node_by_uid(uid, tenant_id)
        typ = (props.get("labels") or [props.get("type") or "Unknown"])[0]
        if typ not in ALLOWED_TYPES:
            continue
        text = props.get("definition") or props.get("method_text") or props.get("payload") or props.get("statement") or props.get("description") or props.get("title") or uid
        items.append((uid, typ, text))

    if not items:
        return {"processed": 0}

    n = 0
    for batch_start in range(0, len(items), BATCH_SIZE):
        batch = items[batch_start : batch_start + BATCH_SIZE]
        texts = [text for _, _, text in batch]

        # Single API call per batch instead of per-entity
        vectors = prov.embed_batch(texts)

        points = []
        for (uid, typ, text), vec in zip(batch, vectors):
            if len(vec) != d:
                vec = (vec[:d] if len(vec) >= d else (vec + [0.0] * (d - len(vec))))
            points.append(PointStruct(
                id=uuid.uuid4(),
                vector=vec,
                payload={"tenant_id": tenant_id, "uid": uid, "type": typ, "text": text},
            ))

        client.upsert(collection_name=name, points=points)
        n += len(points)

    return {"processed": n}
