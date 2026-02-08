"""
Qdrant vector database utilities
Provides functions for upserting and searching vectors in Qdrant
"""

import os
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

# Initialize Qdrant client
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)

try:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=10
    )
    print(f"✅ Connected to Qdrant at {QDRANT_URL}")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to Qdrant: {e}")
    client = None


def ensure_collection_exists(collection_name: str, vector_size: int = 768):
    """Ensure collection exists, create if it doesn't"""
    if not client:
        return False

    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if collection_name not in collection_names:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            print(f"✅ Created collection: {collection_name}")
        return True
    except Exception as e:
        print(f"❌ Error ensuring collection exists: {e}")
        return False


def upsert_point(
    collection: str,
    point_id: str,
    vector: List[float],
    payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Upsert a point (vector + metadata) into Qdrant collection

    Args:
        collection: Collection name
        point_id: Unique point ID
        vector: Vector embedding
        payload: Metadata payload

    Returns:
        Result dictionary with status
    """
    if not client:
        return {
            "status": "error",
            "message": "Qdrant client not initialized"
        }

    try:
        # Ensure collection exists
        vector_size = len(vector)
        ensure_collection_exists(collection, vector_size)

        # Prepare payload
        if payload is None:
            payload = {}

        # Upsert point
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )

        result = client.upsert(
            collection_name=collection,
            points=[point]
        )

        return {
            "status": "success",
            "collection": collection,
            "point_id": point_id,
            "result": str(result)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def search(
    collection: str,
    vector: List[float],
    limit: int = 10,
    filter_payload: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Search for similar vectors in Qdrant collection

    Args:
        collection: Collection name
        vector: Query vector
        limit: Number of results to return
        filter_payload: Optional filter conditions

    Returns:
        Search results with scores
    """
    if not client:
        return {
            "status": "error",
            "message": "Qdrant client not initialized",
            "results": []
        }

    try:
        # Build filter if provided
        query_filter = None
        if filter_payload:
            query_filter = Filter(**filter_payload)

        # Search
        results = client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
            query_filter=query_filter
        )

        # Format results
        formatted_results = []
        for hit in results:
            formatted_results.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            })

        return {
            "status": "success",
            "collection": collection,
            "count": len(formatted_results),
            "results": formatted_results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "results": []
        }


def delete_point(collection: str, point_id: str) -> Dict[str, Any]:
    """Delete a point from collection"""
    if not client:
        return {
            "status": "error",
            "message": "Qdrant client not initialized"
        }

    try:
        client.delete(
            collection_name=collection,
            points_selector=[point_id]
        )

        return {
            "status": "success",
            "collection": collection,
            "point_id": point_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def get_collection_info(collection: str) -> Dict[str, Any]:
    """Get information about a collection"""
    if not client:
        return {
            "status": "error",
            "message": "Qdrant client not initialized"
        }

    try:
        info = client.get_collection(collection_name=collection)

        return {
            "status": "success",
            "collection": collection,
            "info": {
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
